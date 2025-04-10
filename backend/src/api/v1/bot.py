"""
Bot API endpoints (v1)

These endpoints handle WhatsApp webhook interactions via Twilio.
"""

from flask import Blueprint, request, jsonify, current_app
import os
import secrets
import string
from datetime import datetime, timedelta
from twilio.rest import Client
import re
import json
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import google.generativeai as genai
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from ...utils.audit_logger import audit_decorator, log_audit_event
from ...utils.error_handler import api_route_wrapper, BadRequestError, ServerError
from ...models.models import User, KeywordStat, Message, CheckIn
from ...services import queue_sentiment_analysis
from ...services.check_in_flow import handle_check_in_response, handle_timeout_checks

# Create a Blueprint for the bot API
bot_bp = Blueprint('bot_api_v1', __name__)

# Constants
MAX_MESSAGES_PER_DAY = 50
INACTIVITY_THRESHOLD = timedelta(hours=1)

# Initialize Twilio client
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
client = Client(account_sid, auth_token)

# Initialize Gemini AI
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash-002")
except Exception as e:
    current_app.logger.error(f"Failed to initialize Gemini AI: {str(e)}")

def generate_access_code(length=8):
    """Generate a random access code for user authentication"""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_over_message_limit(user):
    """Check if a user has exceeded their daily message limit"""
    # Reset message count if last message was more than 24 hours ago
    if user.last_message_time and (datetime.utcnow() - user.last_message_time) > timedelta(hours=24):
        user.message_count = 0
        return False
    
    # Check if user has exceeded message limit
    return user.message_count >= MAX_MESSAGES_PER_DAY

def update_message_count(user):
    """Update the message count for a user"""
    # If last message was more than 24 hours ago, reset count
    if user.last_message_time and (datetime.utcnow() - user.last_message_time) > timedelta(hours=24):
        user.message_count = 1
    else:
        user.message_count += 1
    
    user.last_message_time = datetime.utcnow()

def get_response(user_input, conversation_history):
    """Get a response from the Gemini AI model"""
    # System prompt is defined in app.py
    system_prompt = current_app.config.get('SYSTEM_PROMPT', "")
    
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{conversation_history}\nUser: {user_input}")
        return response.text
    except google_exceptions.InternalServerError:
        # Fallback response if model has an error
        return "I'm having trouble processing your request right now. Could you please try again in a moment?"
    except Exception as e:
        current_app.logger.error(f"Error getting model response: {str(e)}")
        return "I'm sorry, I'm experiencing some technical difficulties. Please try again later."

def split_message(message, limit=1600):
    """Split a message into chunks if it exceeds the character limit"""
    return [message[i:i+limit] for i in range(0, len(message), limit)]

def get_recent_conversation_history(conversation_history, max_exchanges=10):
    """Get the most recent conversation exchanges"""
    if not conversation_history:
        return ""
    
    exchanges = conversation_history.split('\n\n')
    return '\n\n'.join(exchanges[-max_exchanges:])

def extract_keywords(text):
    """Extract keywords from text for sentiment analysis"""
    try:
        # Tokenize and remove stopwords
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        keywords = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 3]
        
        # Get the most common keywords
        return list(set(keywords))
    except Exception as e:
        current_app.logger.error(f"Error extracting keywords: {str(e)}")
        return []

@bot_bp.route('/bot', methods=['POST'])
@api_route_wrapper
def bot():
    """
    Webhook endpoint for WhatsApp messages via Twilio.
    
    Expected request format:
    {
        "Body": "Message content",
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+0987654321"
    }
    
    Returns:
        Twilio-compatible XML response
    """
    try:
        # Get the database instance from the app
        db = current_app.extensions['sqlalchemy'].db
        
        # Extract message content and sender information
        incoming_msg = request.form.get('Body', '').strip()
        sender = request.form.get('From', '')
        
        if not incoming_msg or not sender:
            raise BadRequestError("Missing required parameters")
        
        # Remove 'whatsapp:' prefix if present
        if sender.startswith('whatsapp:'):
            sender = sender[9:]
        
        # Log the incoming message (anonymized)
        log_audit_event(
            user_id="anonymized", 
            action="receive_message", 
            target="whatsapp_bot",
            details={"message_length": len(incoming_msg)}
        )
        
        # Find or create user
        user = db.session.query(User).filter_by(phone_number=sender).first()
        
        # New user flow
        if not user:
            # Generate access code for new user
            access_code = generate_access_code()
            user = User(
                phone_number=sender,
                access_code=access_code,
                is_authenticated=False,
                conversation_started=False,
                message_count=0
            )
            db.session.add(user)
            db.session.commit()
            
            # Send welcome message with access code
            response_message = (
                f"Welcome to Manobal! Your access code is {access_code}. "
                "Please enter this code to verify your identity."
            )
            
            # Send response via Twilio
            message = client.messages.create(
                from_=f'whatsapp:{twilio_whatsapp_number}',
                body=response_message,
                to=f'whatsapp:{sender}'
            )
            
            return {"status": "success", "message": "Welcome message sent"}
        
        # Authentication flow for existing but unauthenticated users
        if not user.is_authenticated:
            if incoming_msg == user.access_code:
                user.is_authenticated = True
                user.authentication_time = datetime.utcnow()
                db.session.commit()
                
                # Send consent message
                response_message = (
                    "Thank you for authenticating. I'm Manobal, your mental health companion. "
                    "I'm here to chat about how you're feeling and provide support. "
                    "To continue, please provide your consent by replying with:\n\n"
                    "'I consent to Manobal using my anonymized conversation data for mental health insights.'"
                )
                
                # Send response via Twilio
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body=response_message,
                    to=f'whatsapp:{sender}'
                )
                
                return {"status": "success", "message": "User authenticated"}
            else:
                # Send authentication failure message
                response_message = (
                    f"Sorry, that code is incorrect. Your access code is {user.access_code}. "
                    "Please enter this code to verify your identity."
                )
                
                # Send response via Twilio
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body=response_message,
                    to=f'whatsapp:{sender}'
                )
                
                return {"status": "success", "message": "Authentication failed"}
        
        # Consent flow for authenticated users
        if not user.consent_given:
            if "I consent" in incoming_msg.lower():
                user.consent_given = True
                db.session.commit()
                
                # Ask for location and department
                response_message = (
                    "Thank you for your consent. To provide better insights, "
                    "please share your department and location in the format:\n\n"
                    "Department: [Your Department], Location: [Your Location]\n\n"
                    "For example: 'Department: Engineering, Location: Remote'"
                )
                
                # Send response via Twilio
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body=response_message,
                    to=f'whatsapp:{sender}'
                )
                
                return {"status": "success", "message": "Consent received"}
            else:
                # Remind user about consent
                response_message = (
                    "To continue using Manobal, I need your consent. Please reply with:\n\n"
                    "'I consent to Manobal using my anonymized conversation data for mental health insights.'"
                )
                
                # Send response via Twilio
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body=response_message,
                    to=f'whatsapp:{sender}'
                )
                
                return {"status": "success", "message": "Consent reminder sent"}
        
        # Location and department capture for users who haven't provided it yet
        if user.consent_given and (not user.location or not user.department):
            # Check for department and location in the message
            dept_match = re.search(r'department:\s*([^,]+)', incoming_msg, re.IGNORECASE)
            loc_match = re.search(r'location:\s*([^,]+)', incoming_msg, re.IGNORECASE)
            
            if dept_match or loc_match:
                if dept_match:
                    user.department = dept_match.group(1).strip()
                if loc_match:
                    user.location = loc_match.group(1).strip()
                
                db.session.commit()
                
                # Check if we still need more info
                if not user.department or not user.location:
                    missing = []
                    if not user.department:
                        missing.append("department")
                    if not user.location:
                        missing.append("location")
                    
                    response_message = (
                        f"Thank you. Could you please also provide your {' and '.join(missing)}? "
                        "Please use the format:\n\n"
                        f"{'Department: [Your Department], ' if not user.department else ''}"
                        f"{'Location: [Your Location]' if not user.location else ''}"
                    )
                else:
                    # Start the conversation
                    user.conversation_started = True
                    db.session.commit()
                    
                    response_message = (
                        f"Thank you for providing your information. Now I'm ready to chat with you! "
                        "How are you feeling today? You can also type 'start check-in' at any time "
                        "to begin a structured check-in process."
                    )
                
                # Send response via Twilio
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body=response_message,
                    to=f'whatsapp:{sender}'
                )
                
                return {"status": "success", "message": "User information updated"}
            else:
                # Prompt for correctly formatted department and location
                response_message = (
                    "I couldn't detect your department and location in the correct format. "
                    "Please use the format:\n\n"
                    "Department: [Your Department], Location: [Your Location]\n\n"
                    "For example: 'Department: Engineering, Location: Remote'"
                )
                
                # Send response via Twilio
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body=response_message,
                    to=f'whatsapp:{sender}'
                )
                
                return {"status": "success", "message": "Format clarification sent"}
        
        # Check if user has exceeded message limit
        if is_over_message_limit(user):
            response_message = (
                "You've reached the maximum number of messages for today. "
                "Please try again tomorrow."
            )
            
            # Send response via Twilio
            message = client.messages.create(
                from_=f'whatsapp:{twilio_whatsapp_number}',
                body=response_message,
                to=f'whatsapp:{sender}'
            )
            
            return {"status": "success", "message": "Message limit reached"}
            
        # Process check-in flow if user has started a check-in
        check_in_result = handle_check_in_response(user.id, incoming_msg)
        if check_in_result['response_text']:
            # Handle structured check-in flow
            response_message = check_in_result['response_text']
            
            # Save user message to the database
            user_message = Message(
                user_id=user.id,
                content=incoming_msg,
                is_from_user=True,
                department=user.department,
                location=user.location,
                timestamp=datetime.utcnow()
            )
            db.session.add(user_message)
            
            # Save AI response as a message
            ai_message = Message(
                user_id=user.id,
                content=response_message,
                is_from_user=False,
                department=user.department,
                location=user.location,
                timestamp=datetime.utcnow()
            )
            db.session.add(ai_message)
            db.session.commit()
            
            # Queue sentiment analysis for the message if appropriate
            if check_in_result['check_in'] and check_in_result['check_in'].state == 'completed':
                # Extract all text from the check-in for sentiment analysis
                check_in = check_in_result['check_in']
                combined_text = f"{check_in.mood_description or ''} {check_in.stress_factors or ''} {check_in.qualitative_feedback or ''}"
                if combined_text.strip():
                    queue_sentiment_analysis(user_message.id, user.id, combined_text)
            else:
                queue_sentiment_analysis(user_message.id, user.id)
            
            # Split response if it's too long for WhatsApp
            response_chunks = split_message(response_message)
            
            # Send response via Twilio
            for chunk in response_chunks:
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body=chunk,
                    to=f'whatsapp:{sender}'
                )
            
            # Log the response (anonymized)
            log_audit_event(
                user_id="anonymized", 
                action="send_response", 
                target="whatsapp_bot",
                details={"message_length": len(response_message), "chunks": len(response_chunks)}
            )
            
            return {"status": "success", "message": "Check-in response sent"}
        
        # Normal conversation flow
        # Get conversation history or initialize it
        conversation_history = user.conversation_history or ""
        
        # Check if this is a new conversation after inactivity
        if user.last_message_time and (datetime.utcnow() - user.last_message_time) > INACTIVITY_THRESHOLD:
            # Add a separator in the conversation history
            if conversation_history:
                conversation_history += "\n\n--- New Session ---\n\n"
        
        # Add user message to history
        if conversation_history:
            conversation_history += f"\nUser: {incoming_msg}"
        else:
            conversation_history = f"User: {incoming_msg}"
        
        # Get AI response
        recent_history = get_recent_conversation_history(conversation_history)
        ai_response = get_response(incoming_msg, recent_history)
        
        # Add AI response to history
        conversation_history += f"\nAI: {ai_response}"
        
        # Update user record
        user.conversation_history = conversation_history
        update_message_count(user)
        
        # Save user message to the database
        user_message = Message(
            user_id=user.id,
            content=incoming_msg,
            is_from_user=True,
            department=user.department,
            location=user.location,
            timestamp=datetime.utcnow()
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Queue sentiment analysis for the message
        queue_sentiment_analysis(user_message.id, user.id)
        
        # Extract and store keywords for sentiment analysis
        keywords = extract_keywords(incoming_msg)
        
        for keyword in keywords:
            keyword_stat = KeywordStat(
                user_id=user.id,
                department=user.department or "Unknown",
                location=user.location or "Unknown",
                keyword=keyword,
                count=1
            )
            db.session.add(keyword_stat)
        
        # Save AI response as a message
        ai_message = Message(
            user_id=user.id,
            content=ai_response,
            is_from_user=False,
            department=user.department,
            location=user.location,
            timestamp=datetime.utcnow()
        )
        db.session.add(ai_message)
        db.session.commit()
        
        # Split response if it's too long for WhatsApp
        response_chunks = split_message(ai_response)
        
        # Send response via Twilio
        for chunk in response_chunks:
            message = client.messages.create(
                from_=f'whatsapp:{twilio_whatsapp_number}',
                body=chunk,
                to=f'whatsapp:{sender}'
            )
        
        # Log the response (anonymized)
        log_audit_event(
            user_id="anonymized", 
            action="send_response", 
            target="whatsapp_bot",
            details={"message_length": len(ai_response), "chunks": len(response_chunks)}
        )
        
        return {"status": "success", "message": "Response sent"}
    
    except Exception as e:
        current_app.logger.error(f"Error in bot webhook: {str(e)}")
        # Return a safe response even on error
        try:
            if 'sender' in locals() and 'twilio_whatsapp_number' in locals():
                message = client.messages.create(
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    body="I'm having trouble processing your message. Please try again later.",
                    to=f'whatsapp:{sender}'
                )
        except:
            pass
        
        raise

@bot_bp.route('/check-timeout', methods=['GET'])
@api_route_wrapper
def check_timeout():
    """
    Check for timed-out check-in sessions and mark them as expired
    
    This endpoint can be called by a scheduled task to maintain conversation state.
    
    Returns:
        JSON with information about processed timeouts
    """
    result = handle_timeout_checks()
    return jsonify({
        "status": "success",
        "warnings_sent": result['warnings'],
        "expired_sessions": result['expirations']
    }), 200

@bot_bp.route('/send', methods=['POST'])
@api_route_wrapper
@audit_decorator("send", "whatsapp_message")
def send_message():
    """
    Send a message to a WhatsApp user.
    
    Request Body:
    {
        "phone_number": "whatsapp:+1234567890",
        "message": "Hello from Manobal!"
    }
    
    Returns:
        JSON with status and message ID
    """
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequestError("Missing request body")
            
        phone_number = data.get('phone_number')
        message_content = data.get('message')
        
        if not phone_number or not message_content:
            raise BadRequestError("Missing required fields: phone_number, message")
        
        # Ensure phone number has whatsapp: prefix
        if not phone_number.startswith('whatsapp:'):
            phone_number = f'whatsapp:{phone_number}'
            
        # Send message via Twilio
        try:
            message = client.messages.create(
                from_=f'whatsapp:{twilio_whatsapp_number}',
                body=message_content,
                to=phone_number
            )
            
            return {
                "status": "success",
                "message_id": message.sid
            }
        except Exception as e:
            current_app.logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise ServerError("Failed to send WhatsApp message")
    except BadRequestError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error in send message: {str(e)}")
        raise

@bot_bp.route('/status', methods=['POST'])
@api_route_wrapper
def message_status():
    """
    Handle message status updates from WhatsApp.
    
    This endpoint receives status updates from Twilio about message delivery.
    
    Returns:
        JSON with status
    """
    try:
        # Extract status data from request
        message_sid = request.form.get('MessageSid')
        message_status = request.form.get('MessageStatus')
        
        if not message_sid or not message_status:
            raise BadRequestError("Missing required fields: MessageSid, MessageStatus")
        
        # Log status update
        current_app.logger.info(f"Message {message_sid} status: {message_status}")
        
        # In a real implementation, you'd update the message status in your database
        
        return {
            "status": "success",
            "message": "Status update processed"
        }
    except BadRequestError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error processing status update: {str(e)}")
        raise

@bot_bp.route('/template', methods=['POST'])
@api_route_wrapper
@audit_decorator("send", "whatsapp_template")
def send_template():
    """
    Send a template message to a WhatsApp user.
    
    Request Body:
    {
        "phone_number": "whatsapp:+1234567890",
        "template_name": "appointment_reminder",
        "parameters": {
            "name": "John Doe",
            "time": "3:00 PM"
        }
    }
    
    Returns:
        JSON with status and message ID
    """
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequestError("Missing request body")
            
        template_name = data.get('template_name')
        phone_number = data.get('phone_number')
        parameters = data.get('parameters', {})
        
        if not template_name or not phone_number:
            raise BadRequestError("Missing required fields: template_name, phone_number")
        
        # Ensure phone number has whatsapp: prefix
        if not phone_number.startswith('whatsapp:'):
            phone_number = f'whatsapp:{phone_number}'
            
        # In a real implementation, you'd format the template with parameters
        # and send it via Twilio's API
        
        # Placeholder for template implementation
        template_message = f"This is a template message: {template_name}"
        
        if parameters:
            # Simple parameter replacement
            for key, value in parameters.items():
                template_message = template_message.replace(f"{{{key}}}", str(value))
        
        # Send message via Twilio
        try:
            message = client.messages.create(
                from_=f'whatsapp:{twilio_whatsapp_number}',
                body=template_message,
                to=phone_number
            )
            
            return {
                "status": "success",
                "template_name": template_name,
                "message_id": message.sid
            }
        except Exception as e:
            current_app.logger.error(f"Error sending template: {str(e)}")
            raise ServerError("Failed to send template message")
    except BadRequestError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error in send template: {str(e)}")
        raise
