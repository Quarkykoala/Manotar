"""
Error Handler Module for Manobal Platform

Provides structured JSON error responses and exception handling
for the Flask API to ensure consistent error formats across all endpoints.
"""

import logging
import traceback
from functools import wraps
from flask import jsonify, current_app, request
import json
import uuid

# Configure logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors with status code and message"""
    def __init__(self, message, status_code=400, details=None, error_code=None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.error_code = error_code or "API_ERROR"
        super().__init__(self.message)


class BadRequestError(APIError):
    """400 Bad Request Error"""
    def __init__(self, message="Bad request", details=None, error_code="BAD_REQUEST"):
        super().__init__(message, 400, details, error_code)


class UnauthorizedError(APIError):
    """401 Unauthorized Error"""
    def __init__(self, message="Unauthorized", details=None, error_code="UNAUTHORIZED"):
        super().__init__(message, 401, details, error_code)


class ForbiddenError(APIError):
    """403 Forbidden Error"""
    def __init__(self, message="Forbidden", details=None, error_code="FORBIDDEN"):
        super().__init__(message, 403, details, error_code)


class NotFoundError(APIError):
    """404 Not Found Error"""
    def __init__(self, message="Resource not found", details=None, error_code="NOT_FOUND"):
        super().__init__(message, 404, details, error_code)


class ServerError(APIError):
    """500 Internal Server Error"""
    def __init__(self, message="Internal server error", details=None, error_code="SERVER_ERROR"):
        super().__init__(message, 500, details, error_code)


def format_error_response(error, include_traceback=False):
    """
    Format an error as a structured JSON response
    
    Args:
        error: The error object (APIError or other Exception)
        include_traceback: Whether to include the traceback in the response (only in debug mode)
    
    Returns:
        dict: A structured error response
    """
    error_id = str(uuid.uuid4())
    
    # Get status code and error details
    if isinstance(error, APIError):
        status_code = error.status_code
        message = error.message
        error_code = error.error_code
        details = error.details
    else:
        status_code = 500
        message = str(error) or "Internal server error"
        error_code = "SERVER_ERROR"
        details = {}
    
    # Build the response
    response = {
        "success": False,
        "error": {
            "id": error_id,
            "code": error_code,
            "message": message,
            "details": details,
            "status": status_code
        }
    }
    
    # Include traceback in debug mode if requested
    if include_traceback and current_app.debug:
        response["error"]["traceback"] = traceback.format_exc()
    
    return response, status_code


def handle_api_errors(app):
    """
    Register error handlers for a Flask app
    
    Args:
        app: The Flask application instance
    """
    # Register handlers for our custom API errors
    @app.errorhandler(APIError)
    def handle_api_error(error):
        logger.error(f"API Error: {error.message}")
        response, status_code = format_error_response(error)
        return jsonify(response), status_code
    
    # Handle 404 errors
    @app.errorhandler(404)
    def handle_not_found(error):
        logger.error(f"Not Found: {request.path}")
        response, status_code = format_error_response(
            NotFoundError(f"Resource not found: {request.path}")
        )
        return jsonify(response), status_code
    
    # Handle 500 errors
    @app.errorhandler(500)
    def handle_server_error(error):
        logger.error(f"Server Error: {str(error)}")
        response, status_code = format_error_response(
            ServerError("Internal server error"), include_traceback=True
        )
        return jsonify(response), status_code

    # Handle other errors
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled Exception: {str(error)}")
        response, status_code = format_error_response(
            ServerError("Internal server error"), include_traceback=True
        )
        return jsonify(response), status_code


def api_route_wrapper(func):
    """
    Decorator to wrap API routes with try/except and provide consistent JSON responses
    
    Example:
    @app.route('/api/v1/resource')
    @api_route_wrapper
    def get_resource():
        # Function implementation
        pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If the result is already a tuple (response, status_code), return it
            if isinstance(result, tuple) and len(result) == 2:
                return result
            
            # If the result is already a Response object, return it
            if hasattr(result, 'get_data'):
                return result
            
            # Otherwise, assume it's data that needs to be wrapped in a success response
            return jsonify({
                "success": True,
                "data": result
            }), 200
            
        except APIError as e:
            logger.error(f"API Error in {func.__name__}: {str(e)}")
            response, status_code = format_error_response(e)
            return jsonify(response), status_code
            
        except Exception as e:
            logger.error(f"Unhandled Exception in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            response, status_code = format_error_response(
                ServerError(f"Error processing request: {str(e)}"),
                include_traceback=True
            )
            return jsonify(response), status_code
    
    return wrapper 