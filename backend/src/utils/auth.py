"""
Authentication utilities for the Manobal API.

This module provides functions for JWT authentication and
role-based access control.
"""

import os
import random
import string
from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token, verify_jwt_in_request
)
from backend.src.utils.errors import AuthenticationError, AuthorizationError

# Initialize JWT
jwt = JWTManager()

def init_jwt(app):
    """
    Initialize JWT authentication for the Flask application
    
    Args:
        app: Flask application instance
    """
    jwt.init_app(app)
    
    # JWT error handlers
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

def admin_required(fn):
    """
    Decorator for admin-only endpoints
    
    Requires a valid JWT token and admin role
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        if not identity or 'role' not in identity or identity['role'] != 'admin':
            raise AuthorizationError("Admin access required")
        
        return fn(*args, **kwargs)
    return wrapper

def hr_required(fn):
    """
    Decorator for HR-only endpoints
    
    Requires a valid JWT token and HR or admin role
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        if not identity or 'role' not in identity or identity['role'] not in ['hr', 'admin']:
            raise AuthorizationError("HR access required")
        
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
        'role': user.role
    }
    
    access_token = create_access_token(identity=user_claims)
    refresh_token = create_refresh_token(identity=user_claims)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
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