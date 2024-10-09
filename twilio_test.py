from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Use environment variables for sensitive information
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

# Check if credentials are available
if not account_sid or not auth_token:
    raise ValueError("Twilio credentials are missing. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")

client = Client(account_sid, auth_token)

try:
    message = client.messages.create(
        body='Hello from Twilio!',
        from_='whatsapp:+14155238886',  # Twilio Sandbox WhatsApp number
        to='whatsapp:+917710056323'     # Your WhatsApp number
    )
    print(f"Message sent successfully. SID: {message.sid}")
except TwilioRestException as e:
    print(f"An error occurred: {str(e)}")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")