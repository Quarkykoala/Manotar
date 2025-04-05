"""
Error handling utilities for the Manobal API.

This module provides custom error classes and handlers for consistent
error responses across the API.
"""

from flask import jsonify, current_app

# Custom exception classes
class APIError(Exception):
    """Base class for API errors"""
    status_code = 500
    error_code = "SERVER_ERROR"
    message = "An unexpected error occurred"
    
    def __init__(self, message=None, error_code=None, status_code=None, payload=None):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.status_code = status_code or self.status_code
        self.payload = payload
        
    def to_dict(self):
        """Convert error to dictionary for response"""
        error_dict = {
            "error": self.error_code,
            "message": self.message,
            "status": self.status_code
        }
        if self.payload:
            error_dict["details"] = self.payload
        return error_dict


class BadRequestError(APIError):
    """Error for invalid request data"""
    status_code = 400
    error_code = "BAD_REQUEST"
    message = "Invalid request data"


class AuthenticationError(APIError):
    """Error for authentication failures"""
    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "Authentication required"


class AuthorizationError(APIError):
    """Error for permission issues"""
    status_code = 403
    error_code = "FORBIDDEN"
    message = "You don't have permission to access this resource"


class NotFoundError(APIError):
    """Error for resource not found"""
    status_code = 404
    error_code = "NOT_FOUND"
    message = "The requested resource was not found"


class ConflictError(APIError):
    """Error for resource conflicts"""
    status_code = 409
    error_code = "CONFLICT"
    message = "The request conflicts with the current state of the resource"


class ValidationError(BadRequestError):
    """Error for validation failures"""
    error_code = "VALIDATION_ERROR"
    message = "Validation failed"


class ServerError(APIError):
    """Error for server-side issues"""
    status_code = 500
    error_code = "SERVER_ERROR"
    message = "An unexpected server error occurred"


class ServiceUnavailableError(APIError):
    """Error for unavailable services"""
    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"
    message = "The service is currently unavailable"


def init_error_handlers(app):
    """
    Register error handlers for the Flask application
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handler for custom API errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handler for 404 errors"""
        response = jsonify({
            "error": "NOT_FOUND",
            "message": "The requested resource was not found",
            "status": 404
        })
        response.status_code = 404
        return response
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handler for 405 errors"""
        response = jsonify({
            "error": "METHOD_NOT_ALLOWED",
            "message": "The method is not allowed for the requested URL",
            "status": 405
        })
        response.status_code = 405
        return response
    
    @app.errorhandler(500)
    def handle_server_error(error):
        """Handler for 500 errors"""
        current_app.logger.error(f"Unhandled error: {str(error)}")
        response = jsonify({
            "error": "SERVER_ERROR",
            "message": "An unexpected server error occurred",
            "status": 500
        })
        response.status_code = 500
        return response
    
    # Return the app for chaining
    return app 