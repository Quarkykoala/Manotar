"""
Authentication API endpoints (v1)

These endpoints handle user authentication and authorization for the dashboard.
"""

from flask import Blueprint, request, jsonify, current_app
import os
import jwt
from datetime import datetime, timedelta
import bcrypt
from functools import wraps
from ...utils.audit_logger import audit_decorator, log_audit_event
from ...utils.error_handler import api_route_wrapper, UnauthorizedError, BadRequestError, NotFoundError
from ...models.models import AuthUser

# Create a Blueprint for the auth API
auth_bp = Blueprint('auth_api_v1', __name__)

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 24  # hours

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    """Check if a password matches its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(user_id, role):
    """Generate a JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            raise UnauthorizedError('Token is missing')
        
        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload['user_id']
            role = payload['role']
            
            # Log audit event for token usage
            log_audit_event(
                user_id=user_id,
                action="api_access",
                target=request.endpoint,
                details={"role": role, "method": request.method}
            )
            
            # Add user info to request context
            request.user_id = user_id
            request.user_role = role
            
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError('Token has expired')
        except jwt.InvalidTokenError:
            raise UnauthorizedError('Invalid token')
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to restrict routes to admin users only"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user_role != 'admin':
            raise UnauthorizedError('Admin privileges required')
        
        return f(*args, **kwargs)
    
    return decorated

def hr_required(f):
    """Decorator to restrict routes to HR or admin users"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user_role not in ['hr', 'admin']:
            raise UnauthorizedError('HR privileges required')
        
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
@api_route_wrapper
@audit_decorator
def login():
    """
    Login endpoint for dashboard users
    
    Expected request format:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Returns:
        JWT token and user info
    """
    # Get the database instance from the app
    db = current_app.extensions['sqlalchemy'].db
    
    # Get request data
    data = request.json
    if not data:
        raise BadRequestError('No input data provided')
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        raise BadRequestError('Email and password are required')
    
    # Find the user
    user = db.session.query(AuthUser).filter_by(email=email).first()
    
    if not user:
        raise NotFoundError('User not found')
    
    # Check if the password is correct
    if not check_password(password, user.password_hash):
        # Log failed login attempt
        log_audit_event(
            user_id=email,
            action="login_failed",
            target="auth_api",
            details={"reason": "incorrect_password"}
        )
        raise UnauthorizedError('Invalid credentials')
    
    # Generate token
    token = generate_token(user.id, user.role)
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log successful login
    log_audit_event(
        user_id=user.id,
        action="login_success",
        target="auth_api",
        details={"role": user.role}
    )
    
    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }

@auth_bp.route('/register', methods=['POST'])
@api_route_wrapper
@admin_required
@audit_decorator
def register():
    """
    Register a new HR or admin user (admin-only endpoint)
    
    Expected request format:
    {
        "email": "newuser@example.com",
        "name": "New User",
        "password": "password123",
        "role": "hr"  # or "admin"
    }
    
    Returns:
        Created user info
    """
    # Get the database instance from the app
    db = current_app.extensions['sqlalchemy'].db
    
    # Get request data
    data = request.json
    if not data:
        raise BadRequestError('No input data provided')
    
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    role = data.get('role')
    
    if not all([email, name, password, role]):
        raise BadRequestError('Email, name, password, and role are required')
    
    if role not in ['hr', 'admin']:
        raise BadRequestError('Role must be either "hr" or "admin"')
    
    # Check if user already exists
    existing_user = db.session.query(AuthUser).filter_by(email=email).first()
    
    if existing_user:
        raise BadRequestError('User with this email already exists')
    
    # Create new user
    hashed_password = hash_password(password)
    new_user = AuthUser(
        email=email,
        name=name,
        password_hash=hashed_password,
        role=role,
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Log user creation
    log_audit_event(
        user_id=request.user_id,
        action="create_user",
        target=new_user.id,
        details={"role": role}
    )
    
    return {
        "status": "success",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role
        }
    }

@auth_bp.route('/verify-token', methods=['GET'])
@api_route_wrapper
@token_required
def verify_token():
    """
    Verify if the current token is valid
    
    Returns:
        User info for the token
    """
    # Get the database instance from the app
    db = current_app.extensions['sqlalchemy'].db
    
    # Fetch the user
    user = db.session.query(AuthUser).filter_by(id=request.user_id).first()
    
    if not user:
        raise NotFoundError('User not found')
    
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }

@auth_bp.route('/reset-password', methods=['POST'])
@api_route_wrapper
@token_required
@audit_decorator
def reset_password():
    """
    Reset a user's password (requires authentication)
    
    Expected request format:
    {
        "current_password": "oldpassword",
        "new_password": "newpassword"
    }
    
    Returns:
        Success message
    """
    # Get the database instance from the app
    db = current_app.extensions['sqlalchemy'].db
    
    # Get request data
    data = request.json
    if not data:
        raise BadRequestError('No input data provided')
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        raise BadRequestError('Current password and new password are required')
    
    # Fetch the user
    user = db.session.query(AuthUser).filter_by(id=request.user_id).first()
    
    if not user:
        raise NotFoundError('User not found')
    
    # Check if the current password is correct
    if not check_password(current_password, user.password_hash):
        # Log failed password reset attempt
        log_audit_event(
            user_id=user.id,
            action="password_reset_failed",
            target="auth_api",
            details={"reason": "incorrect_current_password"}
        )
        raise UnauthorizedError('Current password is incorrect')
    
    # Update the password
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log successful password reset
    log_audit_event(
        user_id=user.id,
        action="password_reset_success",
        target="auth_api",
        details={}
    )
    
    return {
        "status": "success",
        "message": "Password reset successfully"
    }

@auth_bp.route('/users', methods=['GET'])
@api_route_wrapper
@admin_required
def get_users():
    """
    Get a list of all users (admin-only endpoint)
    
    Returns:
        List of users
    """
    # Get the database instance from the app
    db = current_app.extensions['sqlalchemy'].db
    
    # Fetch all users
    users = db.session.query(AuthUser).all()
    
    user_list = [{
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None
    } for user in users]
    
    return {
        "status": "success",
        "users": user_list
    }

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@api_route_wrapper
@admin_required
@audit_decorator
def delete_user(user_id):
    """
    Delete a user (admin-only endpoint)
    
    Returns:
        Success message
    """
    # Get the database instance from the app
    db = current_app.extensions['sqlalchemy'].db
    
    # Fetch the user
    user = db.session.query(AuthUser).filter_by(id=user_id).first()
    
    if not user:
        raise NotFoundError('User not found')
    
    # Don't allow admins to delete themselves
    if user_id == request.user_id:
        raise BadRequestError('Cannot delete your own account')
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    # Log user deletion
    log_audit_event(
        user_id=request.user_id,
        action="delete_user",
        target=user_id,
        details={"role": user.role}
    )
    
    return {
        "status": "success",
        "message": f"User {user_id} deleted successfully"
    } 