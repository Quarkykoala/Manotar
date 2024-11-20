import os
import secrets
import string
import logging
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect

import re
from dotenv import load_dotenv

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure the database
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_connection_name = os.getenv("DB_CONNECTION_NAME")

# Determine the environment based on the operating system
if os.getenv('GAE_ENV', '').startswith('standard'):
    # Running on Google App Engine, use Unix socket
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_pass}@/{db_name}'
        f'?unix_socket=/cloudsql/{db_connection_name}'
    )
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.info("Operating System: Unix-like")
    logger.info(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
else:
    # Running locally or in a different environment, use TCP connection
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
    )
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.info("Operating System: Windows")
    logger.info(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    access_code = db.Column(db.String(8), nullable=False)
    is_authenticated = db.Column(db.Boolean, default=False)
    conversation_started = db.Column(db.Boolean, default=False)
    last_message_time = db.Column(db.DateTime, nullable=True)
    message_count = db.Column(db.Integer, default=0)
    conversation_history = db.Column(db.Text, nullable=True)
    authentication_time = db.Column(db.DateTime, nullable=True)
    consent_given = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<User {self.phone_number}>'

# Define the KeywordStat model
class KeywordStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<KeywordStat {self.keyword} for User {self.user_id}>'

# Twilio configuration
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

client = Client(account_sid, auth_token)

# Configure the Generative AI library with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Define the system prompt
system_prompt = """
You are Athena, an empathetic and expert mental health support assistant. Provide warm, engaging responses that integrate techniques from various psychological therapies. Offer tailored, actionable advice and maintain a natural conversational flow. Use metaphors and analogies to simplify complex concepts. Be prepared to manage crisis situations and adapt to diverse cultural backgrounds. Promote resilience building and self-care. Use gentle humor when appropriate and convey warmth through text. Be comfortable with ambiguity and employ reflective listening. Recommend professional help when necessary. If a user suggests they are suicidal, provide the suicide prevention number +91-9820466726.
"""

# Define helper functions
def generate_access_code(length=8):
    """Generates a secure random 8-character access code."""
    try:
        characters = string.ascii_letters + string.digits
        code = ''.join(secrets.choice(characters) for _ in range(length))
        logger.info(f"Generated access code: {code}")
        return code
    except Exception as e:
        logger.exception("Error generating access code.")
        raise

def is_over_message_limit(user):
    """
    Check if the user has exceeded their daily message limit.
    """
    try:
        now = datetime.utcnow()
        if user.last_message_time is None or (now - user.last_message_time) >= timedelta(days=1):
            user.message_count = 0
            user.last_message_time = now
            db.session.commit()
            logger.info(f"Reset message count for {user.phone_number} after 24 hours.")
            return False
        else:
            over_limit = user.message_count >= 50
            logger.info(f"User {user.phone_number} message count: {user.message_count}. Over limit: {over_limit}")
            return over_limit
    except Exception as e:
        logger.exception(f"Error checking message limit for user {user.phone_number}: {e}")
        return False

def update_message_count(user):
    """Updates the message count and last message time for the user."""
    try:
        user.message_count += 1
        user.last_message_time = datetime.utcnow()
        db.session.commit()
        logger.info(f"Updated message count for {user.phone_number} to {user.message_count}.")
    except Exception as e:
        logger.exception(f"Error updating message count for user {user.phone_number}: {e}")
        raise

def get_response(user_input, conversation_history):
    """Generates a response from the AI model based on user input and conversation history."""
    try:
        # Construct the conversation including the system prompt
        full_conversation = f"{system_prompt}\n\n{conversation_history}\nUser: {user_input}\nAthena:"
        
        # Generate the response using the model
        response = model.generate_content(full_conversation)
        
        # Extract the assistant's response
        assistant_response = response.text.strip()
        
        # Ensure the response doesn't go beyond "User:"
        if "\nUser:" in assistant_response:
            assistant_response = assistant_response.split("\nUser:")[0]
        
        return assistant_response
    except Exception as e:
        logger.exception(f"Error generating AI response: {str(e)}")
        return "I encountered an error while processing your request. Please try again later."

def split_message(message, limit=1600):
    """Splits a message into chunks of specified character limit."""
    return [message[i:i + limit] for i in range(0, len(message), limit)]

def get_recent_conversation_history(conversation_history, max_exchanges=10):
    """Retrieves the most recent conversation exchanges."""
    exchanges = conversation_history.strip().split('\n')
    recent_exchanges = exchanges[-(max_exchanges * 2):]  # Assuming each exchange has 'User:' and 'Athena:'
    return '\n'.join(recent_exchanges)

def extract_keywords(text):
    keywords_to_monitor = ['overworked', 'stress', 'burnout', 'anxiety', 'deadline', 'pressure', 'workload']
    tokens = word_tokenize(text.lower())
    words = [word for word in tokens if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    keyword_counts = {}
    for keyword in keywords_to_monitor:
        count = filtered_words.count(keyword)
        if count > 0:
            keyword_counts[keyword] = count
    return keyword_counts

# Define routes
AUTHENTICATION_DURATION = timedelta(days=30)  # Example duration

@app.route("/bot", methods=['POST'])
def bot():
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '').strip()

        # Sanitize incoming message
        incoming_msg = re.sub(r'[^\w\s.,!?]', '', incoming_msg)

        # Normalize from_number by stripping 'whatsapp:'
        if from_number.startswith('whatsapp:'):
            from_number = from_number[len('whatsapp:'):]

        logger.info(f"Normalized from_number: {from_number}")
        logger.info(f"Received message from {from_number}: {incoming_msg}")

        if not from_number:
            logger.error("Missing 'From' value in incoming request. Cannot proceed.")
            return "Invalid request", 400

        # Fetch or create user
        user = User.query.filter_by(phone_number=from_number).first()
        if user is None:
            # New user: generate access code and create user record
            access_code = generate_access_code()
            user = User(phone_number=from_number, access_code=access_code, conversation_history="")
            db.session.add(user)
            db.session.commit()
            # Send access code to the user
            message = client.messages.create(
                body=f"Welcome to Athena, your mental health support assistant.\n"
                     f"To begin, please enter your unique access code: {access_code}.\n"
                     f"This helps us ensure your privacy and security.",
                from_=f'whatsapp:{twilio_whatsapp_number}',
                to=f'whatsapp:{from_number}'
            )
            return '', 200
        else:
            logger.info(f"Existing user {from_number} with access code {user.access_code}")

        # Handle 'RESEND' command
        if incoming_msg.upper() == 'RESEND':
            existing_access_code = user.access_code
            message = client.messages.create(
                body=f"Your access code is: {existing_access_code}. Please enter this code to begin.",
                from_=f'whatsapp:{twilio_whatsapp_number}',
                to=f'whatsapp:{from_number}'
            )
            return '', 200

        # Authentication handling
        if not user.is_authenticated:
            if incoming_msg.upper() == user.access_code:
                user.is_authenticated = True
                user.authentication_time = datetime.utcnow()
                db.session.commit()
                message = client.messages.create(
                    body="Access granted. To continue, we need your consent to collect and process your data. Do you agree? (Reply with 'Yes' or 'I agree')",
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    to=f'whatsapp:{from_number}'
                )
                return '', 200
            else:
                message = client.messages.create(
                    body="I'm sorry, but that's not the correct access code. Please check and try again, or type 'RESEND' if you need your code.",
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    to=f'whatsapp:{from_number}'
                )
                return '', 200
        else:
            # Collect consent
            if not user.consent_given:
                if incoming_msg.lower() in ['yes', 'i agree']:
                    user.consent_given = True
                    db.session.commit()
                    message = client.messages.create(
                        body="Thank you for your consent. Please enter the location of your office (e.g., Mumbai):",
                        from_=f'whatsapp:{twilio_whatsapp_number}',
                        to=f'whatsapp:{from_number}'
                    )
                    return '', 200
                else:
                    message = client.messages.create(
                        body="To continue, please provide your consent by replying with 'Yes'.",
                        from_=f'whatsapp:{twilio_whatsapp_number}',
                        to=f'whatsapp:{from_number}'
                    )
                    return '', 200
            # Collect location
            if not user.location:
                user.location = incoming_msg
                db.session.commit()
                message = client.messages.create(
                    body="Please enter your department (e.g., Accounts, HR):",
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    to=f'whatsapp:{from_number}'
                )
                return '', 200
            # Collect department
            if not user.department:
                user.department = incoming_msg
                db.session.commit()
                message = client.messages.create(
                    body="Thank you! You can now start your conversation with Athena. How can I assist you today?",
                    from_=f'whatsapp:{twilio_whatsapp_number}',
                    to=f'whatsapp:{from_number}'
                )
                return '', 200

        # Proceed with conversation
        if is_over_message_limit(user):
            message = client.messages.create(
                body="You have reached your daily message limit. Please try again tomorrow.",
                from_=f'whatsapp:{twilio_whatsapp_number}',
                to=f'whatsapp:{from_number}'
            )
            return '', 200

        update_message_count(user)

        # Use recent conversation history for context
        recent_history = get_recent_conversation_history(user.conversation_history)
        bot_response = get_response(incoming_msg, recent_history)

        # Sanitize bot response
        bot_response = re.sub(r'[^\w\s.,!?]', '', bot_response)

        # Update conversation history
        user.conversation_history = (user.conversation_history or '') + f"\nUser: {incoming_msg}\nAthena: {bot_response}"
        db.session.commit()

        # Extract keywords from the user's message
        keyword_counts = extract_keywords(incoming_msg)

        # Update keyword statistics in the database
        for keyword, count in keyword_counts.items():
            keyword_stat = KeywordStat(
                user_id=user.id,
                department=user.department,
                location=user.location,
                keyword=keyword,
                count=count,
            )
            db.session.add(keyword_stat)
        db.session.commit()

        # Send the response
        messages = split_message(bot_response)
        for msg in messages:
            client.messages.create(
                from_=f'whatsapp:{twilio_whatsapp_number}',
                body=msg,
                to=f'whatsapp:{from_number}'
            )
        return '', 200
    except Exception as e:
        logger.exception(f"Unhandled exception in bot route: {str(e)}")
        return "An internal error occurred. Please try again later.", 500

@app.route("/test", methods=['GET'])
def test():
    test_input = "I am stressed about my job"
    try:
        response_text = get_response(test_input, "")
        return f"Test succeeded: {response_text}", 200
    except Exception as e:
        return f"Test failed: {str(e)}", 500

@app.route('/test_twilio')
def test_twilio():
    try:
        message = client.messages.create(
            body="Test message from Flask app",
            from_=f'whatsapp:{twilio_whatsapp_number}',
            to='whatsapp:+917710056323'  # Replace with your WhatsApp number
        )
        logger.info(f"Test message sent successfully. SID: {message.sid}")
        return f"Message sent successfully. SID: {message.sid}"
    except Exception as e:
        logger.exception("Error in test_twilio route")
        return f"Error: {str(e)}", 500

@app.route('/apply_migrations', methods=['GET'])
def apply_migrations():
    try:
        migrate.upgrade()
        return jsonify({"message": "Migrations applied successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_table')
def check_table():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'user' in tables:
        return "User table exists!"
    else:
        return "User table does not exist."

@app.route('/api/keyword-stats', methods=['GET'])
def get_keyword_stats():
    # For simplicity, this example does not include authentication
    department = request.args.get('department')
    location = request.args.get('location')

    query = db.session.query(
        KeywordStat.keyword,
        db.func.sum(KeywordStat.count).label('total_count')
    )

    if department:
        query = query.filter(KeywordStat.department == department)
    if location:
        query = query.filter(KeywordStat.location == location)

    query = query.group_by(KeywordStat.keyword)
    stats = query.all()

    data = [{'keyword': stat.keyword, 'total_count': stat.total_count} for stat in stats]
    return jsonify(data)

@app.route('/')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
