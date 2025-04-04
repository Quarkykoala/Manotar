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
from ...models.models import User, KeywordStat

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
                        "How are you feeling today?"
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
        db.session.commit()
        
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
