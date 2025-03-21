from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, HRUser

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = HRUser.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = HRUser(username='admin')
            admin.set_password('password123')
            db.session.add(admin)
            try:
                db.session.commit()
                print("Admin user created successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {str(e)}")
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    init_database()
