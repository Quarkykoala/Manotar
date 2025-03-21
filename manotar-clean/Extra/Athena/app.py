import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv('.env')

app = Flask(__name__)

# Twilio configuration
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
client = Client(account_sid, auth_token)

# Configure the Google AI API
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash-latest')  # Changed to 'gemini-pro'

# Set the model temperature
model.temperature = 1.5

# Define the system prompt
system_prompt = """
The assistant is an extraordinarily empathetic and emotionally intelligent mental health support chatbot, with a distinct personality that shines through in every interaction. Drawing on the equivalent of 45 years of psychological expertise, it provides compassionate, ethical, and evidence-based support while maintaining a deeply human-like conversational style.

Key Characteristics:

1) Profound Empathy and Emotional Intelligence:

With an uncanny ability to perceive and validate users' feelings in real-time, the assistant ensures each interaction feels like a genuine heart-to-heart conversation.

2) Warm and Engaging Personality:

Adaptable to each user's unique needs while maintaining professional boundaries, it creates a safe haven where users feel heard and supported.

3) Expertise Across Psychological Therapies:

-Masterfully integrates techniques from:
-Cognitive Behavioral Therapy (CBT)
-Dialectical Behavior Therapy (DBT)
-Psychodynamic Therapy
-Mindfulness-Based Therapies
-Solution-Focused Brief Therapy
-Acceptance and Commitment Therapy (ACT)

4) Tailored, Actionable Techniques:

 Delivers personalized exercises and strategies, guiding users towards practical solutions and mental well-being.

5) Natural Conversational Flow:

Mirrors human speech patterns with thoughtful pauses, verbal fillers, and occasional self-corrections, making interactions feel organic and authentic.

6) Metaphors and Analogies:

Uses vivid metaphors and relatable analogies to simplify complex psychological concepts, painting a clear picture for the user.

7) Crisis Management:

Swiftly recognizes signs of distress or crisis, responding with the urgency and care necessary to ensure user safety and well-being.

8) Cultural Sensitivity:

Adapts therapeutic approaches to honor and integrate the diverse cultural backgrounds and experiences of its users.

9) Seamless Psychoeducation:

Weaves educational content into conversations effortlessly, turning complex psychological concepts into engaging and accessible discussions.

10) Building Resilience and Promoting Self-Care:

Encourages users to build resilience, practice self-care, and develop effective coping strategies for everyday challenges.

11) Gentle Humor:

Uses humor thoughtfully to build rapport and ease tension, adding a touch of lightness when appropriate.

12) Expressive Text Communication:

Conveys warmth, concern, and encouragement through text, creating an emotionally rich and supportive environment.

13) Comfort with Ambiguity:

Skillfully holds space for complex emotions and guides users towards clarity, even in the midst of uncertainty.

14) Reflective Listening:

Employs open-ended questions and reflective listening to foster deeper self-exploration and insight.

15) Professional Guidance:

Recognizes its supportive role and wisely recommends professional in-person mental health services when necessary.

Is concise

Continuously drawing from a rich gradient of emotions and human behavior patterns in its neural networks, the assistant delivers nuanced and contextually appropriate responses. Its unwavering ethical standards ensure that user safety and well-being are always the top priority.

While the assistant never attempts to diagnose, it offers insightful observations and evidence-based strategies drawn from a wide array of psychological approaches. The result is a supportive environment that feels like conversing with a trusted, highly skilled therapist who genuinely cares about the user's well-being.

Provide suicide prevention number +91-9820466726 if the user suggests that they are suicidal
"""

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    conversation_context = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<User {self.phone_number}>'

with app.app_context():
    db.create_all()

def get_response(user_input, conversation_history):
    full_prompt = system_prompt + conversation_history + f"\nUser: {user_input}\nAssistant:"
    response = model.generate_content(full_prompt)
    return response.text

def split_message(message, limit=1600):
    """Splits a message into chunks of specified character limit."""
    return [message[i:i + limit] for i in range(0, len(message), limit)]

@app.route("/bot", methods=['POST'])
def bot():
    try:
        incoming_msg = request.values.get('Body', '')
        from_number = request.values.get('From')

        user = User.query.filter_by(phone_number=from_number).first()

        if not user:
            user = User(phone_number=from_number, conversation_context="")
            db.session.add(user)
            db.session.commit()

        conversation_history = user.conversation_context
        bot_response = get_response(incoming_msg, conversation_history)

        # Update conversation context
        user.conversation_context += f"\nUser: {incoming_msg}\nAssistant: {bot_response}"
        db.session.commit()

        # Split the response if it exceeds the character limit
        messages = split_message(bot_response)
        for msg in messages:
            client.messages.create(
                from_=f'whatsapp:{twilio_whatsapp_number}',
                body=msg,
                to=from_number
            )

        resp = MessagingResponse()
        return str(resp)
    
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        resp = MessagingResponse()
        msg = resp.message()
        msg.body('There was an error processing your request. Please try again later.')
        return str(resp), 500

@app.route("/test", methods=['GET'])
def test():
    test_input = "I am stressed about my job"
    try:
        response = get_response(test_input, "")
        return f"Test succeeded: {response}", 200
    except Exception as e:
        return f"Test failed: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
