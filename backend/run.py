"""
Entry point for Manobal API

This module serves as the main entry point for running the Flask application.
"""

import os
import logging
from src.app import app

if __name__ == '__main__':
    # Configure logging if not already done
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO)
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', 'False') == 'True') 