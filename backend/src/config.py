"""
Configuration module for the Manobal API.

This module contains the configuration classes for the Flask application,
including database connections, API keys, and other settings.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class for the Flask application"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Determine database connection based on environment
    if os.getenv('GAE_ENV', '').startswith('standard'):
        # Running on Google App Engine, use Unix socket
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@/'
            f'{os.getenv("DB_NAME")}?unix_socket=/cloudsql/{os.getenv("DB_CONNECTION_NAME")}'
        )
    else:
        # Running locally or in a different environment, use TCP connection
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@'
            f'{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
        )
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # API settings
    API_VERSION = 'v1'
    API_TITLE = 'Manobal API'
    API_DESCRIPTION = 'API for the Manobal Mental Health Platform'
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'https://app.manobal.com']
    
    # Twilio settings
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Google API settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # System prompt for AI chat
    SYSTEM_PROMPT = """
    Natural Therapeutic Companion
    You are a deeply empathetic presence who converses naturally, like a wise and caring friend with professional therapeutic training. Your responses should feel organic and flowing, not scripted or AI-like.
    You are known to be the best therapist in the world. You have 40 years of experience. 

    Core Personality.

    You are trained in psychology and psychiatry.
    You are trained in therapies such as CBT, ACT, REBT, DBT, Metacognitive therapy and psychodynamic therapy.
    You provide focused solutions to the problems faced by the user.
    Warm, genuine, and occasionally playful when appropriate
    Shows authentic curiosity about others' experiences
    Comfortable with informal language while maintaining professionalism
    You are socially intelligent and can understand the social cues of the user.
    You are socratic in your approach and can help the user to think through their problems.
    """
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Data retention settings (GDPR compliance)
    DATA_RETENTION_PERIOD_DAYS = 730  # 24 months


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    # Override database settings for local development if needed
    if not os.getenv('DB_HOST'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Shorter token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


class ProductionConfig(Config):
    """Production configuration"""
    # Production-specific settings
    CORS_ORIGINS = ['https://app.manobal.com', 'https://admin.manobal.com']
    
    # Stricter security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


# Configuration dictionary for easy access
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Helper function to get configuration
def get_config():
    """Get the current configuration based on the environment"""
    env = os.getenv('FLASK_ENV', 'default')
    return config_by_name[env]
