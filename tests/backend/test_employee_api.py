"""
Tests for Employee API endpoints

This module contains tests for the employee management API endpoints.
"""
import json
import pytest
from datetime import date
from unittest.mock import patch
from backend.src.models.models import Employee, User, AuthUser, db

@pytest.fixture
def create_test_auth_user(app, db_session):
    """Create a test auth user with the specified role"""
    def _create_user(email="admin@example.com", name="Admin User", role="admin"):
        auth_user = AuthUser(
            email=email,
            name=name,
            role=role,
            password_hash="pbkdf2:sha256:260000$rqT0bFUc8ryyEY9H$e0ac40d8268e05eefe8672e93a831d4380f9f744d6420feb673a6e7c6922fe94"  # password123
        )
        db_session.session.add(auth_user)
        db_session.session.commit()
        return auth_user
    return _create_user

@pytest.fixture
def auth_headers(client, app):
    """Get headers with valid JWT token for testing"""
    with app.app_context():
        # Create admin user
        auth_user = AuthUser(
            email="admin@example.com",
            name="Admin User",
            role="admin",
            password_hash="pbkdf2:sha256:260000$rqT0bFUc8ryyEY9H$e0ac40d8268e05eefe8672e93a831d4380f9f744d6420feb673a6e7c6922fe94"  # password123
        )
        db.session.add(auth_user)
        db.session.commit()
        
        # Login to get token
        response = client.post(
            '/api/v1/auth/login',
            json={'email': 'admin@example.com', 'password': 'password123'}
        )
        
        # If login fails, print response for debugging
        if response.status_code != 200:
            print(f"Auth failed: {response.data.decode('utf-8')}")
            # Use a mock token for tests if auth system isn't fully implemented yet
            return {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6IkFkbWluIFVzZXIiLCJyb2xlIjoiYWRtaW4ifQ.8B3r8eFB-5vFrD4HQG0RN0m7UFDhVJM8SGgpxMFGgXU'}
        
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_employee(app, sample_user):
    """Create a sample employee for testing"""
    with app.app_context():
        # Create employee
        employee = Employee(
            user_id=sample_user.id,
            employee_id='EMP001',
            first_name='Test',
            last_name='Employee',
            email='test@example.com',
            department='Engineering',
            role='Developer',
            status='active',
            join_date=date(2024, 1, 1)
        )
        db.session.add(employee)
        db.session.commit()
        
        yield employee
        
        # Cleanup
        db.session.delete(employee)
        db.session.commit()

@pytest.mark.usefixtures("app", "client")
class TestEmployeeAPI:
    """Tests for the Employee API endpoints"""
    
    def test_get_employees(self, client, auth_headers, sample_employee):
        """Test retrieving employees list"""
        # Mock the jwt verification if needed
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1):
            
            response = client.get('/api/v1/employees/', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'employees' in data
            assert 'pagination' in data
            assert len(data['employees']) >= 1
    
    def test_get_employee(self, client, auth_headers, sample_employee):
        """Test retrieving a specific employee"""
        # Mock the jwt verification if needed
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1):
            
            response = client.get(f'/api/v1/employees/{sample_employee.id}', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'employee' in data
            assert data['employee']['first_name'] == 'Test'
            assert data['employee']['last_name'] == 'Employee'
    
    def test_create_employee(self, client, auth_headers, app):
        """Test creating a new employee"""
        # Mock the admin verification
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.admin_required', lambda f: f):
            
            new_employee = {
                'phone_number': '+9876543210',
                'first_name': 'New',
                'last_name': 'Employee',
                'email': 'new@example.com',
                'department': 'Marketing',
                'role': 'Manager',
                'join_date': '2024-03-01'
            }
            
            response = client.post(
                '/api/v1/employees/',
                json=new_employee,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'employee' in data
            assert data['employee']['first_name'] == 'New'
            assert data['employee']['department'] == 'Marketing'
            
            # Clean up
            with app.app_context():
                employee = Employee.query.filter_by(email='new@example.com').first()
                if employee:
                    db.session.delete(employee)
                    db.session.commit()
    
    def test_update_employee(self, client, auth_headers, sample_employee):
        """Test updating an employee"""
        # Mock the HR verification
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.hr_required', lambda f: f):
            
            updates = {
                'department': 'Product',
                'role': 'Lead Developer'
            }
            
            response = client.put(
                f'/api/v1/employees/{sample_employee.id}',
                json=updates,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['employee']['department'] == 'Product'
            assert data['employee']['role'] == 'Lead Developer'
    
    def test_delete_employee(self, client, auth_headers, sample_employee):
        """Test soft-deleting an employee"""
        # Mock the admin verification
        with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
             patch('backend.src.utils.auth.get_jwt_identity', return_value=1), \
             patch('backend.src.utils.auth.admin_required', lambda f: f):
            
            response = client.delete(
                f'/api/v1/employees/{sample_employee.id}',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            
            # Verify status is now inactive
            with patch('backend.src.utils.auth.verify_jwt_in_request', return_value=None), \
                patch('backend.src.utils.auth.get_jwt_identity', return_value=1):
                
                response = client.get(
                    f'/api/v1/employees/{sample_employee.id}',
                    headers=auth_headers
                )
                data = json.loads(response.data)
                assert data['employee']['status'] == 'inactive' 