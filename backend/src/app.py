import os
import secrets
import string
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, Blueprint
from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import sqlalchemy.exc
from sqlalchemy import inspect, text
import re
from dotenv import load_dotenv
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import random
from logging.handlers import RotatingFileHandler
import sys
import time
from backend.src.models.models import db
from backend.src.api import init_app  # Import the API init_app function
from backend.src.utils.auth import init_jwt
from backend.src.utils.errors import init_error_handlers

# Set up logging early
def setup_logging(app):
    """Configure application logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set up file handler for info level logs
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Set up console handler for debug logs in development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Log startup
    app.logger.info('Manobal API starting up...')

def create_app(config=None):
    """
    Create and configure the Flask application
    """
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure the app
    app.config.from_object('backend.src.config.Config')
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    init_jwt(app)
    
    # Initialize error handlers
    init_error_handlers(app)
    
    # Initialize API routes
    init_app(app)  # Use the new init_app function
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        return {"status": "ok", "version": "1.0.0"}
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Run the app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
