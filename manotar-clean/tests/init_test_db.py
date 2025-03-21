from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, HRUser, User, Message, KeywordStat
from flask_login import LoginManager

def create_test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return HRUser.query.get(int(user_id))
    
    return app

def init_test_db():
    app = create_test_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create test HR user
        test_hr = HRUser(username='testuser')
        test_hr.set_password('testpass123')
        db.session.add(test_hr)
        
        # Create test user
        test_user = User(
            phone_number='+1234567890',
            department='Engineering',
            access_code='12345678'
        )
        db.session.add(test_user)
        
        # Create test message
        test_message = Message(
            user_id=1,
            content='Test message with stress and anxiety',
            detected_keywords='stress,anxiety'
        )
        db.session.add(test_message)
        
        # Create test keyword stat
        test_stat = KeywordStat(
            user_id=1,
            keyword='stress',
            count=1
        )
        db.session.add(test_stat)
        
        try:
            db.session.commit()
            print("Test database initialized successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing test database: {str(e)}")
            raise

if __name__ == '__main__':
    init_test_db()
