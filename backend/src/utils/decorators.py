"""
Decorators for the Manobal API.

This module provides decorators for route wrapping, auditing,
and other cross-cutting concerns.
"""

import time
import traceback
from functools import wraps
from flask import request, jsonify, current_app, g
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from backend.src.utils.errors import APIError
from backend.src.models.models import AuditLog, db

def api_route_wrapper(f):
    """
    Decorator for API routes that handles exceptions and adds common response fields
    
    This ensures consistent error handling and response structure across all API endpoints.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        request_id = request.headers.get('X-Request-ID', 'unknown')
        
        try:
            # Execute the route function
            result = f(*args, **kwargs)
            
            # If the result is already a response, return it
            if hasattr(result, 'status_code'):
                return result
            
            # Add standard metadata to dictionary responses
            if isinstance(result, dict):
                if 'error' not in result:
                    # Only add metadata to successful responses
                    execution_time = time.time() - start_time
                    result['_metadata'] = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'request_id': request_id,
                        'execution_time_ms': round(execution_time * 1000, 2)
                    }
                
                # Convert dict to JSON response
                return jsonify(result)
            
            # Return any other response type as is
            return result
            
        except APIError as e:
            # Log custom API errors
            current_app.logger.warning(
                f"API Error ({e.error_code}): {e.message} - "
                f"Path: {request.path}, Method: {request.method}, Request ID: {request_id}"
            )
            response = jsonify(e.to_dict())
            response.status_code = e.status_code
            return response
            
        except Exception as e:
            # Log unhandled exceptions
            current_app.logger.error(
                f"Unhandled exception in {f.__name__}: {str(e)}\n"
                f"Path: {request.path}, Method: {request.method}, Request ID: {request_id}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            error_response = {
                'error': 'SERVER_ERROR',
                'message': 'An unexpected error occurred',
                'status': 500
            }
            
            # Add debug information in non-production environments
            if current_app.config.get('DEBUG', False):
                error_response['debug'] = {
                    'exception': str(e),
                    'traceback': traceback.format_exc().split('\n')
                }
                
            return jsonify(error_response), 500
    
    return decorated_function

def audit_decorator(action_type, resource_type):
    """
    Decorator for auditing API actions
    
    Args:
        action_type: Type of action being performed (e.g., 'create', 'read', 'update', 'delete')
        resource_type: Type of resource being accessed (e.g., 'user', 'employee', 'report')
    """
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            # Get current user from JWT token if available
            user_id = None
            try:
                identity = get_jwt_identity()
                if identity and 'id' in identity:
                    user_id = identity['id']
            except Exception:
                # Authentication error, continue with audit but without user_id
                pass
            
            # Extract relevant request information
            resource_id = kwargs.get('id', None)
            if not resource_id:
                # Try to get ID from request path
                path_parts = request.path.split('/')
                if len(path_parts) > 0:
                    try:
                        # Check if last path part is a number
                        resource_id = int(path_parts[-1])
                    except (ValueError, TypeError):
                        # Not a numeric ID in path
                        pass
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=action_type,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                endpoint=request.endpoint,
                method=request.method,
                request_data=str(request.get_json() if request.is_json else request.args),
                timestamp=datetime.utcnow()
            )
            
            # Store audit log in app context for later use
            g.audit_log = audit_log
            
            try:
                # Execute the route function
                result = f(*args, **kwargs)
                
                # Save audit log with success status
                audit_log.status = 'success'
                if hasattr(result, 'status_code'):
                    audit_log.status_code = result.status_code
                
                db.session.add(audit_log)
                db.session.commit()
                
                return result
                
            except Exception as e:
                # Save audit log with error status
                error_message = str(e)
                if len(error_message) > 255:
                    error_message = error_message[:252] + "..."
                
                audit_log.status = 'error'
                audit_log.error_message = error_message
                
                if hasattr(e, 'status_code'):
                    audit_log.status_code = e.status_code
                else:
                    audit_log.status_code = 500
                
                db.session.add(audit_log)
                db.session.commit()
                
                # Re-raise the exception
                raise
                
        return wrapped_function
    return decorator 