# update_schema.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv('.env')

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

with app.app_context():
    db.drop_all()  # This will delete all existing data!
    db.create_all()

print("Database schema updated successfully.")