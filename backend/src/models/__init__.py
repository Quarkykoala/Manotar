"""
Models package for Manobal Platform

This package contains database models and initialization code.
"""

from .models import db, User, Message, KeywordStat, SentimentLog, AuthUser, AuditLog

def init_db(app):
    """
    Initialize the database with the Flask application
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    # Create all tables if they don't exist
    with app.app_context():
        db.create_all()
        app.logger.info("Database initialized")
