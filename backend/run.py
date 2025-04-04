#!/usr/bin/env python
"""
Main entry point for the Manobal backend Flask application.
This script imports the Flask app from the src package.
"""
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

from src.app import app

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug) 