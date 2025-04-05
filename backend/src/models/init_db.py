"""
Database initialization module for Manobal Platform

This module handles initial database setup and admin user creation.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db, HRUser, AuthUser

def create_app():
    """
    Create a Flask application instance configured for database operations
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Import the config without circular import
    from ..config import Config
    
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_database():
    """
    Initialize the database and create initial admin user if needed
    """
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = HRUser.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = HRUser(username='admin')
            admin.set_password('password123')
            db.session.add(admin)
            try:
                db.session.commit()
                print("Admin user created successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {str(e)}")
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    init_database() 