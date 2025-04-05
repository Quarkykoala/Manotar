"""
Authentication utilities for the Manobal API.

This module provides functions for JWT authentication,
role-based access control, and GDPR compliance.
"""

import os
import re
import random
import string
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify, request, current_app, g
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token, verify_jwt_in_request
)
from backend.src.utils.errors import AuthenticationError, AuthorizationError, ValidationError
from backend.src.models.models import AuthUser, GDPRRequest, db

# Initialize JWT
jwt = JWTManager()

# Input validation patterns
PATTERNS = {
    'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    'phone': re.compile(r'^\+?1?\d{9,15}$'),
    'password': re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$')
}

def init_jwt(app):
    """
    Initialize JWT authentication for the Flask application
    
    Args:
        app: Flask application instance
    """
    jwt.init_app(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).scalar()
        return token is not None
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'TOKEN_EXPIRED',
            'message': 'The token has expired',
            'status': 401
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'INVALID_TOKEN',
            'message': 'Signature verification failed',
            'status': 401
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'MISSING_TOKEN',
            'message': 'Authorization header is missing',
            'status': 401
        }), 401
    
    return app

def validate_input(data, field_type):
    """
    Validate input data against predefined patterns
    
    Args:
        data: Input string to validate
        field_type: Type of field to validate against ('email', 'phone', 'password')
    
    Raises:
        ValidationError: If input doesn't match pattern
    """
    if not data or not isinstance(data, str):
        raise ValidationError(f"Invalid {field_type} format")
    
    pattern = PATTERNS.get(field_type)
    if not pattern or not pattern.match(data):
        raise ValidationError(f"Invalid {field_type} format")
    
    return True

def sanitize_input(data):
    """
    Sanitize input data to prevent XSS and injection attacks
    
    Args:
        data: Input string to sanitize
    
    Returns:
        Sanitized string
    """
    if not data:
        return data
    
    # Remove potentially dangerous characters
    data = re.sub(r'[<>]', '', data)
    # Escape special characters
    data = data.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&#x27;')
    return data

def role_required(*roles):
    """
    Decorator for role-based access control
    
    Args:
        *roles: Variable number of allowed roles
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            if not identity or 'role' not in identity:
                raise AuthorizationError("Invalid token payload")
            
            if identity['role'] not in roles:
                raise AuthorizationError(f"Access restricted. Required roles: {', '.join(roles)}")
            
            # Store user info in Flask's g object
            g.user_id = identity.get('id')
            g.user_role = identity.get('role')
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def check_gdpr_compliance(fn):
    """
    Decorator to check GDPR compliance before accessing user data
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        if not identity or 'id' not in identity:
            raise AuthorizationError("Invalid token payload")
        
        user = AuthUser.query.get(identity['id'])
        if not user:
            raise AuthenticationError("User not found")
        
        # Check if user data should be anonymized
        if user.should_anonymize():
            raise AuthorizationError("Data access restricted due to retention policy")
        
        return fn(*args, **kwargs)
    return wrapper

def generate_access_code(length=6):
    """
    Generate a random alphanumeric access code
    
    Args:
        length: Length of the code (default: 6)
    
    Returns:
        A random alphanumeric string
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_user_tokens(user):
    """
    Create access and refresh tokens for a user
    
    Args:
        user: User object
    
    Returns:
        Dict containing access and refresh tokens
    """
    user_claims = {
        'id': user.id,
        'role': user.role,
        'email': user.email
    }
    
    access_token = create_access_token(identity=user_claims)
    refresh_token = create_refresh_token(identity=user_claims)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }

def extract_token_from_header():
    """
    Extract JWT token from Authorization header
    
    Returns:
        The token string or None if not found
    
    Raises:
        AuthenticationError: If header format is invalid
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise AuthenticationError("Invalid authorization header format")
    
    return parts[1]

class TokenBlocklist(db.Model):
    """Model for tracking revoked tokens"""
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, jti):
        self.jti = jti
        self.created_at = datetime.utcnow()

def revoke_token(jti):
    """Add a token to the blocklist"""
    token = TokenBlocklist(jti=jti)
    db.session.add(token)
    db.session.commit() 