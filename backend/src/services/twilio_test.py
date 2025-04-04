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
<<<<<<< HEAD
    # Verify if the credentials are loaded correctly
    print(f"Using Twilio Account SID: {account_sid[:6]}...{account_sid[-4:]}")
    
=======
>>>>>>> 684b464c7 (Initial commit)
    message = client.messages.create(
        body='Hello from Twilio!',
        from_='whatsapp:+14155238886',  # Twilio Sandbox WhatsApp number
        to='whatsapp:+917710056323'     # Your WhatsApp number
    )
    print(f"Message sent successfully. SID: {message.sid}")
<<<<<<< HEAD
    print("Message status:", message.status)
except TwilioRestException as e:
    print(f"Twilio Error: {str(e)}")
    print(f"Error Code: {e.code}")
    print(f"Error Message: {e.msg}")
    if e.code == 21608:
        print("Error: You need to join the WhatsApp sandbox first.")
        print("Please send 'join <sandbox-code>' to +14155238886 on WhatsApp")
    elif e.code == 21211:
        print("Error: Invalid 'To' phone number. Make sure you've joined the sandbox with this number")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
    print(f"Error type: {type(e).__name__}")
=======
except TwilioRestException as e:
    print(f"An error occurred: {str(e)}")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
>>>>>>> 684b464c7 (Initial commit)
