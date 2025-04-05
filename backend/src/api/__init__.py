"""
API initialization module for the Manobal platform.

This module initializes the API blueprints and middleware.
"""

import os
from flask import Flask, Blueprint, g, request, current_app
import logging
from backend.src.api.v1 import v1_bp
from backend.src.api.v1.bot import bot
from backend.src.api.v1.dashboard import dashboard
from backend.src.api.v1.employees import employees
from backend.src.api.v1.gdpr import gdpr
from backend.src.utils.auth import init_jwt

def create_api_blueprint():
    """
    Create and configure the API blueprint with all routes
    """
    # Create the main API blueprint
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    # Register the v1 blueprint
    api_bp.register_blueprint(v1_bp)
    
    return api_bp

def init_api(app: Flask):
    """
    Initialize API routes and middleware
    
    Args:
        app: Flask application instance
    """
    # Initialize JWT
    init_jwt(app)
    
    # Register blueprints
    app.register_blueprint(bot, url_prefix='/api/v1/bot')
    app.register_blueprint(dashboard, url_prefix='/api/v1/dashboard')
    app.register_blueprint(employees, url_prefix='/api/v1/employees')
    app.register_blueprint(gdpr, url_prefix='/api/v1/gdpr')
    
    # Configure GDPR exports directory
    gdpr_exports_dir = os.path.join(app.instance_path, 'gdpr_exports')
    if not os.path.exists(gdpr_exports_dir):
        os.makedirs(gdpr_exports_dir)
    app.config['GDPR_EXPORTS_DIR'] = gdpr_exports_dir
    
    # Register the API blueprint
    api_bp = create_api_blueprint()
    app.register_blueprint(api_bp)
    
    # Register middleware to add API version header
    @app.after_request
    def add_api_version_header(response):
        """Add API version header to responses"""
        if request.path.startswith('/api/'):
            # Extract version from path
            parts = request.path.split('/')
            if len(parts) > 2 and parts[2].startswith('v'):
                version = parts[2]
                response.headers['X-API-Version'] = version
                
                # Mark v1 as deprecated when v2 is released
                if version == 'v1':
                    response.headers['X-API-Deprecated'] = 'true'
                    response.headers['X-API-Deprecation-Date'] = '2024-12-31'
        
        return response
    
    # Log registered routes
    if app.debug:
        for rule in app.url_map.iter_rules():
            app.logger.debug(f"Route: {rule.rule} [{', '.join(rule.methods)}]")
    
    return app 