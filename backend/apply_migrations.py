"""
Apply database migrations for the Manobal application

This script runs Flask-Migrate to apply database migrations
within the Flask application context.
"""
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.app import app
from flask_migrate import Migrate
import alembic
import alembic.config

def apply_migrations():
    """Apply all database migrations using Alembic directly"""
    print("Starting migration process...")
    
    # Create a new Alembic config
    alembic_cfg = alembic.config.Config("../migrations/alembic.ini")
    
    # Override the script location to point to our migrations folder
    alembic_cfg.set_main_option("script_location", "../migrations")
    
    # Run the migrations with the app context
    with app.app_context():
        print(f"Applying migrations to database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Run the migration in offline mode through Alembic directly
        alembic.command.upgrade(alembic_cfg, "update_models_for_api_v1")
        
        print("Migrations applied successfully!")

if __name__ == "__main__":
    apply_migrations() 