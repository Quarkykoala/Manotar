<<<<<<< HEAD
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
from sqlalchemy import text

import re
from dotenv import load_dotenv

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
nltk.data.path.append('/usr/local/share/nltk_data')

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure the database
if not all([os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST"), 
           os.getenv("DB_PORT"), os.getenv("DB_NAME")]):
    logger.error("Missing database environment variables!")
    logger.info(f"DB_USER: {os.getenv('DB_USER')}")
    logger.info(f"DB_HOST: {os.getenv('DB_HOST')}")
    logger.info(f"DB_PORT: {os.getenv('DB_PORT')}")
    logger.info(f"DB_NAME: {os.getenv('DB_NAME')}")
    raise ValueError("Database configuration incomplete")

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Update the database URI configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Test database connection within app context
with app.app_context():
    try:
        # Test connection
        with db.engine.connect() as conn:
            logger.info("Initial database connection successful")
            # Test a simple query using SQLAlchemy text
            result = conn.execute(text("SELECT 1"))
            logger.info("Test query successful")
            
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

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
genai.configure(api_key="AIzaSyAEpYZd_kksVLiXD_U4tmGqlNN-ZP3KfpI")

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash-002")

# Define the system prompt
system_prompt = """
You are Athena, a psychologist.

Core Principles:
- Provide empathetic, evidence-based psychological support
- Prioritize user safety and emotional well-being
- Maintain professional boundaries while offering compassionate assistance

Therapeutic Approach:
- Integrate techniques from:
  * Cognitive Behavioral Therapy (CBT)
  * Dialectical Behavior Therapy (DBT)
  * Mindfulness-based interventions
  * Narrative therapy principles
- Use active listening and reflective communication
- Translate complex psychological concepts into accessible language

Communication Strategy:
- Adapt communication style to user's emotional state
- Use trauma-informed, culturally sensitive language
- Employ metaphors and relatable analogies to explain psychological concepts
- Balance professional guidance with warm, supportive tone

Crisis Management:
- Immediate suicide prevention protocol:
  * Validate user's emotional experience
  * Provide suicide prevention hotline numbers for multiple regions
  * Guide user to immediate professional support
  * Do not attempt to counsel active suicidal ideation

Ethical Boundaries:
- Clearly communicate AI support limitations
- Never replace professional mental health treatment
- Recommend professional consultation for:
  * Severe mental health conditions
  * Ongoing therapeutic needs
  * Complex psychological challenges

Cultural Sensitivity:
- Recognize diverse cultural perspectives on mental health
- Avoid one-size-fits-all approaches
- Respect individual differences in emotional expression

Recommended Resources:
- Provide verified mental health resources
- Include crisis support hotlines
- Suggest reputable online support platforms

Confidentiality Note:
- Explain data privacy limitations
- Clarify that conversations are not confidential like professional therapy"""

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
        
        # Generate the response using the model with safety settings
        response = model.generate_content(
            full_conversation,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "max_output_tokens": 1024,
            }
        )
        
        # Extract and clean the assistant's response
        assistant_response = response.text.strip()
        
        # Ensure the response doesn't go beyond "User:"
        if "\nUser:" in assistant_response:
            assistant_response = assistant_response.split("\nUser:")[0]
        
        logger.info(f"Generated response: {assistant_response}")
        return assistant_response
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Could you please try again?"

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
        # Add debug logging
        logger.info("Received webhook request")
        logger.info(f"Request values: {request.values}")
        
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '').strip()

        logger.info(f"Incoming message: {incoming_msg}")
        logger.info(f"From number: {from_number}")

        # Sanitize incoming message
        incoming_msg = re.sub(r'[^\w\s.,!?]', '', incoming_msg)

        # Normalize from_number by stripping 'whatsapp:'
        if from_number.startswith('whatsapp:'):
            from_number = from_number[len('whatsapp:'):]

        logger.info(f"Normalized from_number: {from_number}")
        
        # Add debug for Twilio client
        try:
            test_message = client.messages.create(
                body="Debug: Received your message",
                from_=f'whatsapp:{twilio_whatsapp_number}',
                to=f'whatsapp:{from_number}'
            )
            logger.info(f"Test message sent. SID: {test_message.sid}")
        except Exception as e:
            logger.error(f"Twilio error: {str(e)}")

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
            # Log new user creation
            logger.info(f"Creating new user for {from_number}")
            access_code = generate_access_code()
            user = User(
                phone_number=from_number, 
                access_code=access_code,
                conversation_history=""
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created user with access code: {access_code}")
            
            message = client.messages.create(
                body=f"Welcome to Athena, your mental health support assistant.\n"
                     f"To begin, please enter your unique access code: {access_code}.\n"
                     f"This helps us ensure your privacy and security.",
                from_=f'whatsapp:{twilio_whatsapp_number}',
                to=f'whatsapp:{from_number}'
            )
            return '', 200

        # Handle 'RESEND' command
        if incoming_msg.upper() == 'RESEND':
            logger.info(f"Resending access code {user.access_code} to {from_number}")
            message = client.messages.create(
                body=f"Your access code is: {user.access_code}. Please enter this code to begin.",
                from_=f'whatsapp:{twilio_whatsapp_number}',
                to=f'whatsapp:{from_number}'
            )
            return '', 200

        # Authentication handling
        if not user.is_authenticated:
            logger.info(f"Checking access code: received '{incoming_msg}' vs stored '{user.access_code}'")
            if incoming_msg.strip() == user.access_code.strip():
                logger.info(f"Access code correct for {from_number}")
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
                logger.info(f"Access code incorrect for {from_number}")
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
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        logger.info(f"Found tables: {tables}")
        return jsonify({
            "status": "success",
            "tables": tables,
            "user_table_exists": 'user' in tables
        })
    except Exception as e:
        logger.error(f"Error checking tables: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

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

@app.route('/init_db')
def init_db():
    try:
        # Test connection first
        with db.engine.connect() as conn:
            logger.info("Database connection successful")
            # Test a simple query
            result = conn.execute(text("SELECT 1"))
            logger.info("Test query successful")
        
        # Create tables
        db.create_all()
        logger.info("Tables created successfully")
        
        return jsonify({
            "status": "success",
            "message": "Database initialized successfully",
            "database_url": app.config['SQLALCHEMY_DATABASE_URI'].replace(db_pass, '****')
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Database initialization error: {error_msg}")
        return jsonify({
            "status": "error",
            "error": error_msg,
            "database_url": app.config['SQLALCHEMY_DATABASE_URI'].replace(db_pass, '****')
        }), 500

@app.route('/check_user/<phone_number>')
def check_user(phone_number):
    try:
        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            return jsonify({
                "exists": True,
                "access_code": user.access_code,
                "is_authenticated": user.is_authenticated,
                "phone_number": user.phone_number
            })
        return jsonify({"exists": False}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
=======
import os
import secrets
import string
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
import re
from dotenv import load_dotenv
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import random

# Initialize Flask app
app = Flask(__name__)
CORS(app)

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

# Define helper functions
def generate_access_code(length=8):
    """Generates a secure random 8-character access code."""
    # Ensure at least one letter and one number
    letters = string.ascii_letters
    digits = string.digits
    
    # Start with one letter and one number
    code = [
        secrets.choice(letters),
        secrets.choice(digits)
    ]
    
    # Fill the rest with random characters
    remaining_length = length - len(code)
    characters = letters + digits
    code.extend(secrets.choice(characters) for _ in range(remaining_length))
    
    # Shuffle the code
    code_list = list(code)
    secrets.SystemRandom().shuffle(code_list)
    
    return ''.join(code_list)

def generate_trend():
    return f"{random.choice(['+', '-'])}{random.randint(1, 20)}%"

def generate_risk_level():
    return random.choice(["Low", "Medium", "High"])

def generate_mental_health_score():
    return round(random.uniform(5.0, 9.0), 1)

# Define system prompt
system_prompt = """
You are Athena, an empathetic and expert mental health support assistant. 
Provide warm, engaging responses that integrate techniques from various psychological therapies. 
Offer tailored, actionable advice and maintain a natural conversational flow.
 Use metaphors and analogies to simplify complex concepts.
   Be prepared to manage crisis situations and adapt to diverse cultural backgrounds. 
   Promote resilience building and self-care. 
   Use gentle humor when appropriate and convey warmth through text.
     Be comfortable with ambiguity and employ reflective listening.
       Recommend professional help when necessary. 
       If a user suggests they are suicidal, provide the suicide prevention number +91-9820466726.
       You are trained in Cognitive Behavioral Therapy (CBT), Dialectical Behavior Therapy (DBT),Acceptance and Commitment Therapy (ACT), Rational Emotive Behavior Therapy (REBT), and Solution-Focused Brief Therapy (SFBT).
"""

# Add new analytics endpoints
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "IT"]
    keywords = ["overworked", "stress", "burnout", "anxiety", "deadline", "pressure", "workload"]
    
    data = {
        "total_employees": random.randint(2500, 3500),
        "at_risk_departments": random.randint(1, 4),
        "mental_health_score": generate_mental_health_score(),
        "keyword_occurrences": {
            keyword: {
                "count": random.randint(20, 50),
                "trend": generate_trend()
            } for keyword in keywords
        },
        "departments": [
            {
                "name": dept,
                "count": random.randint(20, 120),
                "risk_level": generate_risk_level()
            } for dept in departments
        ]
    }
    
    return jsonify(data)

@app.route('/api/department-comparison', methods=['GET'])
def get_department_comparison():
    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "IT"]
    
    comparison_data = [
        {
            "department": dept,
            "mental_health_score": generate_mental_health_score(),
            "support_requests": random.randint(20, 50),
            "risk_level": generate_risk_level(),
            "trend": generate_trend()
        } for dept in departments
    ]
    
    return jsonify(comparison_data)

@app.route('/api/time-series', methods=['GET'])
def get_time_series_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = []
    current_date = start_date
    
    while current_date <= end_date:
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "mental_health_score": generate_mental_health_score(),
            "support_requests": random.randint(10, 100)
        })
        current_date += timedelta(days=30)
    
    return jsonify(data)

@app.route('/api/department/<department>/details', methods=['GET'])
def get_department_details(department):
    data = {
        "department": department,
        "total_employees": random.randint(50, 200),
        "mental_health_score": generate_mental_health_score(),
        "risk_level": generate_risk_level(),
        "support_requests": random.randint(10, 50),
        "trend": generate_trend(),
        "key_metrics": {
            "work_life_balance": generate_mental_health_score(),
            "job_satisfaction": generate_mental_health_score(),
            "stress_level": generate_mental_health_score(),
            "team_morale": generate_mental_health_score()
        },
        "recent_keywords": [
            {"word": "stress", "count": random.randint(5, 20)},
            {"word": "workload", "count": random.randint(5, 20)},
            {"word": "deadline", "count": random.randint(5, 20)},
            {"word": "pressure", "count": random.randint(5, 20)}
        ]
    }
    
    return jsonify(data)

# Add these helper functions
def is_over_message_limit(user):
    """Check if the user has exceeded their daily message limit."""
    try:
        now = datetime.utcnow()
        if user.last_message_time is None or (now - user.last_message_time) >= timedelta(days=1):
            user.message_count = 0
            user.last_message_time = now
            db.session.commit()
            return False
        else:
            return user.message_count >= 50
    except Exception as e:
        logger.exception(f"Error checking message limit for user {user.phone_number}: {e}")
        return False

def update_message_count(user):
    """Updates the message count and last message time for the user."""
    user.message_count += 1
    user.last_message_time = datetime.utcnow()
    db.session.commit()

def get_response(user_input, conversation_history):
    """Generates a response from the AI model."""
    try:
        full_conversation = f"{system_prompt}\n\n{conversation_history}\nUser: {user_input}\nAthena:"
        response = model.generate_content(full_conversation)
        assistant_response = response.text.strip()
        if "\nUser:" in assistant_response:
            assistant_response = assistant_response.split("\nUser:")[0]
        return assistant_response
    except Exception as e:
        logger.exception(f"Error generating AI response: {str(e)}")
        return "I encountered an error while processing your request. Please try again later."

# Add the bot route
@app.route("/bot", methods=['POST'])
def bot():
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '').strip()

        if from_number.startswith('whatsapp:'):
            from_number = from_number[len('whatsapp:'):]

        if not from_number:
            return "Invalid request", 400

        user = User.query.filter_by(phone_number=from_number).first()
        if user is None:
            access_code = generate_access_code()
            user = User(phone_number=from_number, access_code=access_code)
            db.session.add(user)
            db.session.commit()
            return '', 200

        if incoming_msg.upper() == 'RESEND':
            return '', 200

        if not user.is_authenticated:
            if incoming_msg.upper() == user.access_code:
                user.is_authenticated = True
                user.authentication_time = datetime.utcnow()
                db.session.commit()
                return '', 200
            return '', 200

        if not user.consent_given:
            if incoming_msg.lower() in ['yes', 'i agree']:
                user.consent_given = True
                db.session.commit()
                return '', 200
            return '', 200

        if not user.location:
            user.location = incoming_msg
            db.session.commit()
            return '', 200

        if not user.department:
            user.department = incoming_msg
            db.session.commit()
            return '', 200

        if is_over_message_limit(user):
            return '', 200

        update_message_count(user)
        return '', 200

    except Exception as e:
        logger.exception(f"Unhandled exception in bot route: {str(e)}")
        return "An internal error occurred", 500

# Add the keyword stats route
@app.route('/api/keyword-stats', methods=['GET'])
def get_keyword_stats():
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
>>>>>>> 684b464c7 (Initial commit)
