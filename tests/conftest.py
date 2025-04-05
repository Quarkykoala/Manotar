"""
Pytest configuration file for Manobal tests.

This module contains shared fixtures and configuration for all tests.
"""

import os
import pytest
import sys
from unittest.mock import MagicMock
from dotenv import load_dotenv
from sqlalchemy import text

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import backend application 
from backend.src.app import app as flask_app
from backend.src.models.models import db, User, KeywordStat, Message

# Load test environment variables
load_dotenv('.env.test')

def clear_db():
    """Helper function to clear database tables in correct order"""
    try:
        # Disable foreign key checks
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        db.session.commit()

        # Clear tables in correct order
        KeywordStat.query.delete()
        Message.query.delete()
        User.query.delete()
        
        db.session.commit()

        # Re-enable foreign key checks
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

@pytest.fixture(scope='function')
def app():
    """Create and configure a Flask app for testing."""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret_key',
    })
    
    with flask_app.app_context():
        # Create all tables
        db.create_all()
        
        # Clear any existing data
        clear_db()
        
        yield flask_app
        
        # Clean up
        clear_db()
        db.session.remove()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Database session for testing."""
    with app.app_context():
        yield db

@pytest.fixture(scope='function')
def sample_user(app, db_session):
    with app.app_context():
        # Create new user
        user = User(
            phone_number='+1234567890',
            access_code='TEST1234',
            department='Engineering',
            location='Mumbai'
        )
        db_session.session.add(user)
        db_session.session.commit()
        
        yield user

@pytest.fixture
def mock_twilio():
    """Mock Twilio client for testing."""
    mock = MagicMock()
    mock.messages.create.return_value = MagicMock(sid="MOCK_SID")
    return mock

@pytest.fixture
def mock_gemini():
    """Mock Gemini model for testing."""
    mock = MagicMock()
    mock.generate_content.return_value = MagicMock(
        text="I understand you're feeling stressed. That's completely normal. Would you like to talk about what's causing your stress?"
    )
    return mock

@pytest.fixture
def sample_employee_data():
    """Sample employee data for testing."""
    return {
        'name': 'Test Employee',
        'department': 'Engineering',
        'phone_number': 'whatsapp:+1234567890',
        'consent_given': True
    }

@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        'from_user': 'whatsapp:+1234567890',
        'to_user': 'whatsapp:+0987654321',
        'body': 'I am feeling stressed today',
        'direction': 'incoming'
    }