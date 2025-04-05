import pytest
from app import User

def test_bot_endpoint_new_user(test_client, test_app, test_db):
    with test_app.app_context():
        response = test_client.post('/bot', data={
            'Body': 'Hello',
            'From': 'whatsapp:+1234567890'
        })
        assert response.status_code == 200
        
        user = User.query.filter_by(phone_number='+1234567890').first()
        assert user is not None
        assert len(user.access_code) == 8

def test_bot_endpoint_authentication(test_client, test_app, test_db):
    with test_app.app_context():
        user = User(
            phone_number='+1234567890',
            access_code='TEST1234'
        )
        test_db.session.add(user)
        test_db.session.commit()

        response = test_client.post('/bot', data={
            'Body': 'TEST1234',
            'From': 'whatsapp:+1234567890'
        })
        assert response.status_code == 200
        
        user = User.query.filter_by(phone_number='+1234567890').first()
        assert user.is_authenticated

def test_bot_endpoint_consent(test_client, test_app, test_db):
    with test_app.app_context():
        user = User(
            phone_number='+1234567890',
            access_code='TEST1234',
            is_authenticated=True
        )
        test_db.session.add(user)
        test_db.session.commit()

        response = test_client.post('/bot', data={
            'Body': 'Yes',
            'From': 'whatsapp:+1234567890'
        })
        assert response.status_code == 200
        
        user = User.query.filter_by(phone_number='+1234567890').first()
        assert user.consent_given