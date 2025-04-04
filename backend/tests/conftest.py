"""
Pytest configuration file for Manobal tests.

This module contains shared fixtures and configuration for all tests.
"""

import pytest
import os
import sys
from unittest.mock import MagicMock

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import app as flask_app
from src.models import db as _db

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret_key',
    })

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Database session for testing."""
    with app.app_context():
        yield _db


@pytest.fixture
def mock_twilio():
    """Mock Twilio client for testing."""
    mock = MagicMock()
    mock.messages.create.return_value = MagicMock(sid="MOCK_SID")
    return mock


@pytest.fixture
def mock_hume_api():
    """Mock Hume API responses for testing."""
    mock_response = {
        'sentiment_score': 0.75,
        'emotions': {
            'joy': 0.8,
            'excitement': 0.7,
            'admiration': 0.5
        },
        'source': 'hume_api',
        'timestamp': '2023-07-01T12:00:00Z'
    }
    return mock_response


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