"""
Audit Logger for Manobal Platform

This module provides GDPR-compliant audit logging capabilities,
tracking access and modifications to sensitive data with appropriate
user, timestamp, action, and target information.
"""

import logging
import json
import os
from datetime import datetime
from functools import wraps
import uuid
from flask import request, g, current_app

# Configure the audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Create a file handler for the audit log
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(os.path.join(log_dir, "audit.log"))
file_handler.setLevel(logging.INFO)

# Create a formatter and set it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the handler to the logger
audit_logger.addHandler(file_handler)

def log_audit_event(user_id, action, target, details=None, ip_address=None):
    """
    Log an audit event with user_id, timestamp, action, and target.
    
    Args:
        user_id (str): The ID of the user performing the action
        action (str): The action being performed (e.g., "access", "modify", "delete")
        target (str): The target of the action (e.g., "employee_data", "sentiment_log")
        details (dict, optional): Additional details about the action
        ip_address (str, optional): The IP address of the user
    """
    event_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    event = {
        "event_id": event_id,
        "timestamp": timestamp,
        "user_id": user_id,
        "action": action,
        "target": target,
        "ip_address": ip_address or request.remote_addr if request else "unknown",
        "details": details or {}
    }
    
    # Log to audit log file
    audit_logger.info(json.dumps(event))
    
    # Also store in database if available
    try:
        if current_app and hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
            db = current_app.extensions['sqlalchemy'].db
            from ..models.models import AuditLog
            
            # Create a new AuditLog record
            audit_log = AuditLog(
                user_id=user_id if user_id != "anonymized" and user_id != "anonymous" else None,
                action=action,
                target=target,
                details=json.dumps(details) if details else None,
                ip_address=ip_address or request.remote_addr if request else "unknown",
                timestamp=datetime.utcnow()
            )
            
            # Add and commit to the database
            db.session.add(audit_log)
            db.session.commit()
    except Exception as e:
        # Log any errors but don't fail the request
        if current_app:
            current_app.logger.error(f"Error saving audit log to database: {str(e)}")
    
    return event_id

def audit_decorator(func):
    """
    Decorator for auditing API endpoints.
    
    This version automatically extracts endpoint information for logging.
    
    Example:
        @app.route('/api/v1/resource')
        @audit_decorator
        def get_resource():
            # Function implementation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the user ID from the request context if available via JWT auth
        user_id = getattr(request, "user_id", None) if request else None
        
        if not user_id and request:
            # Try to get from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # We have a token but can't decode it here, use a placeholder
                user_id = "authenticated"
        
        if not user_id:
            user_id = "anonymous"
        
        # Determine the action from the HTTP method
        action_map = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        
        action = action_map.get(request.method, "access") if request else "access"
        
        # Get the target from the endpoint and path
        target = request.endpoint if request else func.__name__
        path = request.path if request else ""
        
        # Log the event before executing the function
        details = {
            "method": request.method if request else "",
            "path": path,
            "query_params": dict(request.args) if request and request.args else {},
            # Don't log request body data for privacy reasons
        }
        
        log_audit_event(user_id, action, target, details)
        
        # Execute the function
        result = func(*args, **kwargs)
        return result
    
    return wrapper

# Example of usage:
# @audit_decorator("access", "employee_data")
# def get_employee_data():
#     # Function implementation
#     pass
