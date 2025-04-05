"""
Tests for Check-In API Endpoints

This module contains tests for the check-in API endpoints, including listing, 
viewing details, and retrieving statistics.
"""
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from backend.src.models.models import CheckIn, User, Employee, AuthUser, db

@pytest.fixture
def auth_headers(client, app):
    """Get headers with valid JWT token for testing"""
    with app.app_context():
        # Create HR user
        auth_user = AuthUser(
            email="hr@example.com",
            name="HR User",
            role="hr",
            password_hash="pbkdf2:sha256:260000$rqT0bFUc8ryyEY9H$e0ac40d8268e05eefe8672e93a831d4380f9f744d6420feb673a6e7c6922fe94"  # password123
        )
        db.session.add(auth_user)
        db.session.commit()
        
        # Login to get token
        response = client.post(
            '/api/v1/auth/login',
            json={'email': 'hr@example.com', 'password': 'password123'}
        )
        
        # If login fails, print response for debugging
        if response.status_code != 200:
            print(f"Auth failed: {response.data.decode('utf-8')}")
            # Use a mock token for tests if auth system isn't fully implemented yet
            return {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6IkhSIFVzZXIiLCJyb2xlIjoiaHIifQ.8B3r8eFB-5vFrD4HQG0RN0m7UFDhVJM8SGgpxMFGgXU'}
        
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_user(app, db_session):
    """Create a test user for check-in tests"""
    with app.app_context():
        user = User(
            phone_number='+1234567890',
            department='Engineering',
            location='Remote',
            is_authenticated=True,
            consent_given=True,
            conversation_started=True
        )
        db_session.session.add(user)
        db_session.session.commit()
        yield user

@pytest.fixture
def test_employee(app, db_session, test_user):
    """Create a test employee linked to the test user"""
    with app.app_context():
        employee = Employee(
            user_id=test_user.id,
            employee_id='EMP001',
            first_name='Test',
            last_name='Employee',
            email='test@example.com',
            department='Engineering',
            role='Developer',
            status='active',
            join_date=datetime.now().date()
        )
        db_session.session.add(employee)
        db_session.session.commit()
        yield employee

@pytest.fixture
def sample_check_ins(app, db_session, test_user, test_employee):
    """Create sample check-ins for testing"""
    with app.app_context():
        # Create completed check-in
        completed_check_in = CheckIn(
            user_id=test_user.id,
            employee_id=test_employee.id,
            state='completed',
            is_completed=True,
            mood_score=4,
            mood_description='Feeling productive',
            stress_level=2,
            stress_factors='Minor deadline pressure',
            qualitative_feedback='Good team support this week',
            sentiment_score=0.75,
            created_at=datetime.utcnow() - timedelta(days=1),
            completed_at=datetime.utcnow() - timedelta(days=1, hours=1)
        )
        
        # Create in-progress check-in
        in_progress_check_in = CheckIn(
            user_id=test_user.id,
            employee_id=test_employee.id,
            state='mood_captured',
            is_completed=False,
            mood_score=3,
            created_at=datetime.utcnow(),
            last_interaction_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        
        # Create follow-up required check-in
        follow_up_check_in = CheckIn(
            user_id=test_user.id,
            employee_id=test_employee.id,
            state='completed',
            is_completed=True,
            mood_score=2,
            mood_description='Feeling overwhelmed',
            stress_level=4,
            stress_factors='Too many projects at once',
            qualitative_feedback='Need help prioritizing tasks',
            sentiment_score=0.3,
            follow_up_required=True,
            created_at=datetime.utcnow() - timedelta(days=2),
            completed_at=datetime.utcnow() - timedelta(days=2, hours=1)
        )
        
        db_session.session.add_all([completed_check_in, in_progress_check_in, follow_up_check_in])
        db_session.session.commit()
        
        yield {
            'completed': completed_check_in,
            'in_progress': in_progress_check_in,
            'follow_up': follow_up_check_in
        }

@pytest.mark.usefixtures("app", "client")
class TestCheckInAPI:
    """Tests for the Check-In API endpoints"""
    
    def test_get_check_ins(self, client, auth_headers, sample_check_ins):
        """Test retrieving check-ins list"""
        # Mock the jwt verification if needed
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.hr_required', lambda f: f):
            
            response = client.get('/api/v1/check-ins/', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'check_ins' in data
            assert 'pagination' in data
            assert len(data['check_ins']) >= 3
    
    def test_get_check_ins_with_filters(self, client, auth_headers, sample_check_ins, test_employee):
        """Test retrieving check-ins with filters"""
        # Mock the jwt verification if needed
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.hr_required', lambda f: f):
            
            # Test completed filter
            response = client.get(
                '/api/v1/check-ins/?completed=true',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['check_ins']) >= 2
            assert all(check_in['is_completed'] for check_in in data['check_ins'])
            
            # Test follow-up filter
            response = client.get(
                '/api/v1/check-ins/?follow_up_required=true',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['check_ins']) >= 1
            assert all(check_in['follow_up_required'] for check_in in data['check_ins'])
            
            # Test employee filter
            response = client.get(
                f'/api/v1/check-ins/?employee_id={test_employee.id}',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert all('employee' in check_in for check_in in data['check_ins'])
    
    def test_get_check_in_details(self, client, auth_headers, sample_check_ins):
        """Test retrieving a specific check-in"""
        # Mock the jwt verification if needed
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.hr_required', lambda f: f):
            
            # Get details for the completed check-in
            check_in_id = sample_check_ins['completed'].id
            response = client.get(f'/api/v1/check-ins/{check_in_id}', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'check_in' in data
            assert data['check_in']['id'] == check_in_id
            assert data['check_in']['state'] == 'completed'
            assert 'mood_score' in data['check_in']
            assert 'employee' in data['check_in']
            
            # Test invalid ID
            response = client.get('/api/v1/check-ins/9999', headers=auth_headers)
            assert response.status_code == 404
    
    def test_update_follow_up(self, client, auth_headers, sample_check_ins):
        """Test updating follow-up status"""
        # Mock the jwt verification if needed
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.hr_required', lambda f: f):
            
            # Update the completed check-in with follow-up
            check_in_id = sample_check_ins['completed'].id
            update_data = {
                'follow_up_required': True,
                'follow_up_notes': 'Schedule a call to discuss workload'
            }
            
            response = client.put(
                f'/api/v1/check-ins/{check_in_id}/follow-up',
                json=update_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'check_in' in data
            assert data['check_in']['follow_up_required'] is True
            assert data['check_in']['follow_up_notes'] == 'Schedule a call to discuss workload'
    
    def test_get_statistics(self, client, auth_headers, sample_check_ins):
        """Test retrieving check-in statistics"""
        # Mock the jwt verification if needed
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.hr_required', lambda f: f):
            
            response = client.get('/api/v1/check-ins/statistics', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'total_check_ins' in data
            assert 'avg_mood' in data
            assert 'avg_stress' in data
            assert 'mood_distribution' in data
            assert 'stress_distribution' in data
            assert 'time_series' in data
            
            # Test with department filter
            response = client.get(
                '/api/v1/check-ins/statistics?department=Engineering',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert json.loads(response.data)['department'] == 'Engineering'
            
            # Test with invalid group_by
            response = client.get(
                '/api/v1/check-ins/statistics?group_by=invalid',
                headers=auth_headers
            )
            
            assert response.status_code == 400 