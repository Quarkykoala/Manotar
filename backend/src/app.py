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

# Create Flask application
def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///manobal.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    
    # Set up logging
    setup_logging(app)
    
    # Initialize CORS
    CORS(app)
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    app.extensions['sqlalchemy'] = db
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    app.extensions['migrate'] = migrate
    
    # Download NLTK resources if they don't exist
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        app.logger.info('Downloading nltk punkt tokenizer')
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        app.logger.info('Downloading nltk stopwords')
        nltk.download('stopwords')
    
    # System prompt for AI chat
    app.config['SYSTEM_PROMPT'] = """
    You are Manobal, a mental health support bot. Your role is to:
    
    1. Be compassionate and supportive to users experiencing mental health challenges
    2. Ask questions to understand the user's current mental state better
    3. Provide practical coping strategies and resources
    4. Never diagnose medical conditions or replace professional mental health care
    5. Maintain confidentiality and privacy
    6. Express empathy and validate the user's feelings
    7. Be culturally sensitive and inclusive
    
    If a user expresses thoughts of self-harm or suicide, gently encourage them to seek 
    immediate professional help and provide crisis resources.
    """
    
    # Define a simple startup route
    @app.route('/')
    def index():
        return jsonify({
            "name": "Manobal API",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "docs": "/api/docs"
        })
    
    # Register error handlers
    from .utils.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Initialize database models
    from .models import init_db
    init_db(app)
    
    # Register API blueprints
    from .api import register_blueprints
    register_blueprints(app)
    
    # Initialize async worker for background tasks
    from .services import init_async_worker
    init_async_worker(app)
    
    # Add a simple health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0
        })
    
    # Store startup time
    app.start_time = time.time()
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Run the app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
