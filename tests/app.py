import os
import secrets
import string
import logging
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template, redirect, url_for
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect

import re
from dotenv import load_dotenv

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Set the NLTK data path
nltk.data.path.insert(0, os.path.join(os.path.dirname(__file__), 'nltk_data'))

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # This allows all origins
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'hr_login'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models after initializing db to avoid circular imports
from models import User, Message, KeywordStat, HRUser

# Twilio configuration
client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

# Configure the Generative AI library with your API key
genai.configure(api_key=app.config['GOOGLE_API_KEY'])

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-002-flash")

# Define the system prompt
system_prompt = """
You are Athena, an empathetic and expert mental health support assistant. Provide warm, engaging responses that integrate techniques from various psychological therapies. Offer tailored, actionable advice and maintain a natural conversational flow. Use metaphors and analogies to simplify complex concepts. Be prepared to manage crisis situations and adapt to diverse cultural backgrounds. Promote resilience building and self-care. Use gentle humor when appropriate and convey warmth through text. Be comfortable with ambiguity and employ reflective listening. Recommend professional help when necessary. If a user suggests they are suicidal, provide the suicide prevention number +91-9820466726.
"""

# Define the list of keywords to track
KEYWORDS_TO_TRACK = ['overworked', 'stress', 'burnout', 'anxiety', 'deadline', 'pressure', 'workload']

# Helper functions
def generate_access_code(length=8):
    """Generates a secure random 8-character access code."""
    characters = string.ascii_letters + string.digits
    code = ''.join(secrets.choice(characters) for _ in range(length))
    logger.info(f"Generated access code: {code}")
    return code

def is_over_message_limit(user):
    """Check if the user has exceeded their daily message limit."""
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

def update_message_count(user):
    """Updates the message count and last message time for the user."""
    user.message_count += 1
    user.last_message_time = datetime.utcnow()
    db.session.commit()
    logger.info(f"Updated message count for {user.phone_number} to {user.message_count}.")

def get_response(user_input, conversation_history):
    """Generates a response from the AI model based on user input and conversation history."""
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

def split_message(message, limit=1600):
    """Splits a message into chunks of specified character limit."""
    return [message[i:i + limit] for i in range(0, len(message), limit)]

def detect_keywords(text):
    """Detects predefined keywords in the text."""
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    detected = [word for word in filtered_tokens if word in KEYWORDS_TO_TRACK]
    return detected

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return HRUser.query.get(int(user_id))

@app.route('/hr/login', methods=['GET', 'POST'])
def hr_login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            logger.info(f"Login attempt for username: {username}")
            
            hr_user = HRUser.query.filter_by(username=username).first()
            if hr_user and hr_user.check_password(password):
                login_user(hr_user)
                logger.info(f"Successful login for user: {username}")
                return redirect(url_for('hr_dashboard'))
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                return "Invalid credentials", 401
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in login route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/hr/dashboard')
@login_required
def hr_dashboard():
    try:
        # Get basic metrics
        total_employees = User.query.count()
        active_users = User.query.filter(
            User.last_message_time >= datetime.utcnow() - timedelta(days=7)
        ).count()

        # Get keyword data
        keyword_data = db.session.query(
            User.department,
            Message.detected_keywords,
            db.func.count(Message.id).label('count')
        ).join(Message).group_by(
            User.department,
            Message.detected_keywords
        ).all()

        # Process keyword data for visualization
        keyword_counts = {}
        for department, keywords, count in keyword_data:
            if keywords:
                for keyword in keywords.split(','):
                    key = f"{department},{keyword.strip()}"
                    keyword_counts[key] = count

        return render_template(
            'dashboard.html',
            keyword_counts=keyword_counts,
            total_employees=total_employees,
            active_users=active_users
        )
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        return "An error occurred loading the dashboard", 500

@app.route('/hr/logout')
@login_required
def hr_logout():
    logout_user()
    return redirect(url_for('hr_login'))

# Bot route
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

        user = User.query.filter_by(phone_number=from_number).first()

        if user:
            # User exists, proceed with conversation
            if is_over_message_limit(user):
                client.messages.create(
                    body="You have reached your daily message limit. Please try again tomorrow.",
                    from_=f'whatsapp:{app.config["TWILIO_WHATSAPP_NUMBER"]}',
                    to=f'whatsapp:{from_number}'
                )
                return '', 200

            update_message_count(user)

            # Detect keywords in the user's message
            detected_keywords = detect_keywords(incoming_msg)

            # Save the message to the database
            message_record = Message(
                user_id=user.id,
                content=incoming_msg,
                detected_keywords=','.join(detected_keywords)
            )
            db.session.add(message_record)
            db.session.commit()

            bot_response = get_response(incoming_msg, user.conversation_history or '')

            # Sanitize bot response
            bot_response = re.sub(r'[^\w\s.,!?]', '', bot_response)

            user.conversation_history = (user.conversation_history or '') + f"\nUser: {incoming_msg}\nAthena: {bot_response}"
            db.session.commit()

            # Update keyword statistics in the database
            for keyword in detected_keywords:
                keyword_stat = KeywordStat(
                    user_id=user.id,
                    keyword=keyword,
                    count=1,
                )
                db.session.add(keyword_stat)
            db.session.commit()

            messages = split_message(bot_response)
            for msg in messages:
                client.messages.create(
                    from_=f'whatsapp:{app.config["TWILIO_WHATSAPP_NUMBER"]}',
                    body=msg,
                    to=f'whatsapp:{from_number}'
                )
            return '', 200
        else:
            # New user, create user and send welcome message
            access_code = generate_access_code()
            user = User(phone_number=from_number, access_code=access_code, conversation_history="")
            db.session.add(user)
            db.session.commit()

            welcome_message = (
                f"Welcome to Athena, your mental health support assistant.\n"
                f"To begin, please enter your unique access code: {access_code}.\n"
                f"This helps us ensure your privacy and security."
            )
            client.messages.create(
                body=welcome_message,
                from_=f'whatsapp:{app.config["TWILIO_WHATSAPP_NUMBER"]}',
                to=f'whatsapp:{from_number}'
            )
            return '', 200

    except Exception as e:
        logger.exception(f"Unhandled exception in bot route: {str(e)}")
        return "An internal error occurred. Please try again later.", 500

# API route to get keyword statistics
@app.route("/api/keyword-stats", methods=['GET'])
def get_keyword_stats():
    logger.info("Received request for /api/keyword-stats")
    try:
        # Retrieve keyword statistics
        keyword_data = db.session.query(
            KeywordStat.keyword,
            db.func.sum(KeywordStat.count).label('total_count')
        ).group_by(KeywordStat.keyword).all()

        data = [{'keyword': stat.keyword, 'total_count': stat.total_count} for stat in keyword_data]
        logger.info(f"Returning data: {data}")
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in get_keyword_stats: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Add a test route to verify the server is running
@app.route("/test", methods=['GET'])
def test():
    return jsonify({"message": "Server is running"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
