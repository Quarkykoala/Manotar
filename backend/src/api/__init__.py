"""
API package initializer

This file sets up the API package and registers versioned API blueprints.
"""
from flask import Blueprint

# Main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_blueprints(app):
    """
    Register all API blueprints with the Flask app
    
    Args:
        app: Flask application instance
    """
    # Import versioned API blueprints
    from .v1.dashboard import dashboard_bp
    from .v1.bot import bot_bp
    from .v1.auth import auth_bp
    
    # Register v1 API blueprints
    v1_bp = Blueprint('v1', __name__, url_prefix='/v1')
    v1_bp.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    v1_bp.register_blueprint(bot_bp, url_prefix='/bot')
    v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Register the v1 blueprint with the main API blueprint
    api_bp.register_blueprint(v1_bp)
    
    # Register the main API blueprint with the app
    app.register_blueprint(api_bp)
    
    # Log registered routes
    app.logger.info("API routes registered:")
    for rule in app.url_map.iter_rules():
        app.logger.info(f"{rule.endpoint}: {rule}") 