"""
Database schema update utility

This script updates the database schema for user records.
Run as a standalone script to recreate the database or update 
its structure after model changes.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import sys
import pathlib

# Add parent directory to path to enable importing from parent modules
parent_dir = str(pathlib.Path(__file__).parent.parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Load environment from root .env or backend .env
if os.path.exists('../../../.env'):
    load_dotenv('../../../.env')
elif os.path.exists('../../.env'):
    load_dotenv('../../.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    conversation_context = db.Column(db.Text, nullable=True)
    access_code = db.Column(db.String(6), nullable=True)
    last_message_time = db.Column(db.DateTime, nullable=True)
    message_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.phone_number}>'

if __name__ == "__main__":
    # Only execute when run directly, not when imported
    with app.app_context():
        db.drop_all()  # This will delete all existing data!
        db.create_all()
        print("Database schema updated successfully.")