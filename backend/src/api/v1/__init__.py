"""
API v1 package initializer

This file marks the v1 API directory as a Python package.
"""

from flask import Blueprint

from backend.src.api.v1.auth import auth_bp
from backend.src.api.v1.employees import employees_bp
from backend.src.api.v1.bot import bot_bp
from backend.src.api.v1.dashboard import dashboard_bp

# Create the v1 API blueprint
v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

# Register the blueprints
v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(employees_bp)
v1_bp.register_blueprint(bot_bp)
v1_bp.register_blueprint(dashboard_bp)

# Global routes
@v1_bp.route('/version', methods=['GET'])
def version():
    """Return the current API version information"""
    return {
        "version": "1.0.0",
        "name": "Manobal API",
        "status": "stable",
        "deprecated": False,
        "documentation": "/docs/api/v1"
    }
