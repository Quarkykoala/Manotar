import os
import google.generativeai as genai

# Load environment variables
api_key = os.getenv('GOOGLE_AI_API_KEY')
genai.configure(api_key=api_key)

# Function to list available models
def list_models():
    try:
        available_models = genai.list_models()
        print("Available models:")
        for model in available_models:
            print(f"- {model.name}")
    except Exception as e:
        print("Failed to retrieve models. Error:", str(e))

# Call the function to list models
list_models()