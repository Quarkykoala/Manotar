import os
import pytest
from app import app, db, User, KeywordStat
from dotenv import load_dotenv
from sqlalchemy import text

# Load test environment variables
load_dotenv('.env.test')

def clear_db():
    """Helper function to clear database tables in correct order"""
    try:
        # Disable foreign key checks
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        db.session.commit()

        # Clear tables in correct order
        KeywordStat.query.delete()
        User.query.delete()
        
        db.session.commit()

        # Re-enable foreign key checks
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

@pytest.fixture(scope='function')
def test_app():
    # Configure app for testing
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': (
            f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}'
            f'@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}_test'
        ),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Clear any existing data
        clear_db()
        
        yield app
        
        # Clean up
        clear_db()

@pytest.fixture(scope='function')
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def test_db(test_app):
    with test_app.app_context():
        # Clear any existing data
        clear_db()
        
        yield db
        
        # Clean up after test
        clear_db()

@pytest.fixture(scope='function')
def sample_user(test_app, test_db):
    with test_app.app_context():
        # Create new user
        user = User(
            phone_number='+1234567890',
            access_code='TEST1234',
            department='Engineering',
            location='Mumbai'
        )
        test_db.session.add(user)
        test_db.session.commit()
        
        yield user
        
        # Clean up
        clear_db()