from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50))
    location = db.Column(db.String(50))
    access_code = db.Column(db.String(8))
    is_authenticated = db.Column(db.Boolean, default=False)
    authentication_time = db.Column(db.DateTime)
    consent_given = db.Column(db.Boolean, default=False)
    conversation_started = db.Column(db.Boolean, default=False)
    message_count = db.Column(db.Integer, default=0)
    last_message_time = db.Column(db.DateTime)
    conversation_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = db.relationship('Message', backref='user', lazy=True)
    keywords = db.relationship('KeywordStat', backref='user', lazy=True)
    sentiment_logs = db.relationship('SentimentLog', backref='user', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_from_user = db.Column(db.Boolean, default=True)
    detected_keywords = db.Column(db.String(255))
    sentiment_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    department = db.Column(db.String(50))
    location = db.Column(db.String(50))

class KeywordStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(50))
    location = db.Column(db.String(50))
    keyword = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SentimentLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(50))
    location = db.Column(db.String(50))
    sentiment_score = db.Column(db.Float, nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.relationship('Message', backref='sentiment', uselist=False)

class AuthUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'hr'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    audit_logs = db.relationship('AuditLog', backref='auth_user', lazy=True)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class HRUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
