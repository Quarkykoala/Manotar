from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
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
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'hr', 'bot'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    data_retention_consent = db.Column(db.Boolean, default=False)
    data_retention_consent_date = db.Column(db.DateTime)
    data_retention_expiry = db.Column(db.DateTime)
    is_anonymized = db.Column(db.Boolean, default=False)
    audit_logs = db.relationship('AuditLog', backref='auth_user', lazy=True)
    gdpr_requests = db.relationship('GDPRRequest', backref='auth_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_data_retention_consent(self, consent=True, retention_months=24):
        """Set user's data retention consent and calculate expiry"""
        self.data_retention_consent = consent
        self.data_retention_consent_date = datetime.utcnow()
        if consent:
            self.data_retention_expiry = self.data_retention_consent_date + timedelta(days=retention_months * 30)
        else:
            self.data_retention_expiry = None

    def should_anonymize(self):
        """Check if user data should be anonymized based on retention policy"""
        if not self.data_retention_consent:
            return True
        if self.data_retention_expiry and datetime.utcnow() > self.data_retention_expiry:
            return True
        return False

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

class Employee(db.Model):
    """
    Employee model representing users who interact with the mental health bot
    
    This extends the basic User model with additional professional information.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic information
    employee_id = db.Column(db.String(50), unique=True)  # Employee ID in HR system
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    
    # Organizational information
    department = db.Column(db.String(100))
    role = db.Column(db.String(100))
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Status information
    status = db.Column(db.String(20), default='active')  # active, inactive, on_leave
    join_date = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='employee_profile', uselist=False)
    reports = db.relationship('Employee', backref=db.backref('manager', remote_side=[id]))
    check_ins = db.relationship('CheckIn', backref='employee', lazy=True)
    
    def to_dict(self):
        """Convert employee object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'department': self.department,
            'role': self.role,
            'manager_id': self.manager_id,
            'status': self.status,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'phone_number': self.user.phone_number if self.user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CheckIn(db.Model):
    """
    Structured check-in model for gathering consistent employee mental health data
    
    This model represents a structured check-in session with specific questions about
    mood, stress levels, and qualitative feedback.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Check-in state
    state = db.Column(db.String(50), default='initiated')  # initiated, mood_captured, stress_captured, feedback_captured, completed
    is_completed = db.Column(db.Boolean, default=False)
    
    # Check-in responses
    mood_score = db.Column(db.Integer)  # Scale of 1-5
    mood_description = db.Column(db.Text)  # Qualitative description of mood
    stress_level = db.Column(db.Integer)  # Scale of 1-5
    stress_factors = db.Column(db.Text)  # Factors contributing to stress
    qualitative_feedback = db.Column(db.Text)  # Open feedback
    
    # System-generated analysis
    sentiment_score = db.Column(db.Float)  # Overall sentiment analysis of the check-in
    recommendations = db.Column(db.Text)  # Auto-generated recommendations
    follow_up_required = db.Column(db.Boolean, default=False)  # Flag for HR attention
    follow_up_notes = db.Column(db.Text)  # Notes about any follow-up actions
    
    # Timeout tracking
    last_interaction_time = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # When this check-in session expires
    is_expired = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='check_ins')
    # employee is defined above with Employee model
    
    def to_dict(self):
        """Convert check-in object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'state': self.state,
            'is_completed': self.is_completed,
            'mood_score': self.mood_score,
            'mood_description': self.mood_description,
            'stress_level': self.stress_level,
            'stress_factors': self.stress_factors,
            'qualitative_feedback': self.qualitative_feedback,
            'sentiment_score': self.sentiment_score,
            'recommendations': self.recommendations,
            'follow_up_required': self.follow_up_required,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_expired': self.is_expired
        }

class GDPRRequest(db.Model):
    """Model for tracking GDPR-related data requests"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  # 'export', 'delete', 'access'
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)  # 30 days from request
    data_url = db.Column(db.String(500))  # For export requests
    notes = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set due date to 30 days from request
        self.due_date = self.requested_at + timedelta(days=30)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'request_type': self.request_type,
            'status': self.status,
            'requested_at': self.requested_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'due_date': self.due_date.isoformat(),
            'data_url': self.data_url,
            'notes': self.notes
        }
