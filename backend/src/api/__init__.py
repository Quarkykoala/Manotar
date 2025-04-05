"""
API package initializer

This file sets up the API package and registers versioned API blueprints.
"""
from flask import Flask, Blueprint, g, request, current_app
import logging
from backend.src.api.v1 import v1_bp

def create_api_blueprint():
    """
    Create and configure the API blueprint with all routes
    """
    # Create the main API blueprint
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    # Register the v1 blueprint
    api_bp.register_blueprint(v1_bp)
    
    return api_bp

def init_app(app: Flask):
    """
    Initialize the API with the Flask application
    """
    # Register the API blueprint
    api_bp = create_api_blueprint()
    app.register_blueprint(api_bp)
    
    # Register middleware to add API version header
    @app.after_request
    def add_api_version_header(response):
        """Add API version header to all responses from versioned API endpoints"""
        if request.path.startswith('/api/v'):
            # Extract version from path
            path_parts = request.path.split('/')
            if len(path_parts) > 2:
                version = path_parts[2]  # '/api/v1/...' -> 'v1'
                
                # Add version header
                response.headers['X-API-Version'] = version
                
                # Add deprecation header if needed
                if version == 'v1':
                    # v1 is not deprecated yet
                    response.headers['X-API-Deprecated'] = 'false'
                else:
                    # Future versions may deprecate older ones
                    pass
                    
        return response
    
    # Log all registered routes for debugging
    @app.before_first_request
    def log_routes():
        """Log all registered routes for debugging"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
        
        app.logger.info(f"Registered routes:\n" + "\n".join(routes))
    
    return app 