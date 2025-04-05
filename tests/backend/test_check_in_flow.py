"""
Tests for Check-In Flow

This module contains tests for the structured check-in flow, including state
transitions and conversation timeouts.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from backend.src.models.models import User, CheckIn, db
from backend.src.services.check_in_flow import (
    get_active_check_in, 
    create_check_in, 
    update_check_in_state,
    handle_check_in_response,
    handle_timeout_checks,
    CHECK_IN_STATES,
    RESPONSES
)

@pytest.fixture
def test_user(app, db_session):
    """Create a test user for check-in flow tests"""
    with app.app_context():
        user = User(
            phone_number='+1234567890',
            department='Test Department',
            location='Test Location',
            is_authenticated=True,
            consent_given=True,
            conversation_started=True
        )
        db_session.session.add(user)
        db_session.session.commit()
        yield user
        # Clean up check-ins associated with this user
        CheckIn.query.filter_by(user_id=user.id).delete()
        db_session.session.commit()

@pytest.fixture
def active_check_in(app, db_session, test_user):
    """Create an active check-in for the test user"""
    with app.app_context():
        check_in = CheckIn(
            user_id=test_user.id,
            state='initiated',
            is_completed=False,
            last_interaction_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        db_session.session.add(check_in)
        db_session.session.commit()
        yield check_in

class TestCheckInFlow:
    """Tests for the check-in flow functionality"""
    
    def test_get_active_check_in(self, app, test_user, active_check_in):
        """Test retrieving an active check-in"""
        with app.app_context():
            # Should retrieve the active check-in
            check_in = get_active_check_in(test_user.id)
            assert check_in is not None
            assert check_in.id == active_check_in.id
            assert check_in.state == 'initiated'
            
            # Mark check-in as expired
            active_check_in.is_expired = True
            db.session.commit()
            
            # Should not retrieve expired check-in
            check_in = get_active_check_in(test_user.id)
            assert check_in is None
            
            # Restore check-in status for other tests
            active_check_in.is_expired = False
            db.session.commit()
    
    def test_create_check_in(self, app, test_user):
        """Test creating a new check-in"""
        with app.app_context():
            # Delete any existing check-ins for clean test
            CheckIn.query.filter_by(user_id=test_user.id).delete()
            db.session.commit()
            
            check_in = create_check_in(test_user.id)
            assert check_in is not None
            assert check_in.user_id == test_user.id
            assert check_in.state == 'initiated'
            assert check_in.is_completed is False
            
            # Should have expiration time set
            assert check_in.expires_at is not None
            assert check_in.expires_at > datetime.utcnow()
    
    def test_update_check_in_state(self, app, active_check_in):
        """Test updating check-in state"""
        with app.app_context():
            # Update state to mood_captured
            updated = update_check_in_state(
                active_check_in.id,
                'mood_captured',
                mood_score=4
            )
            
            assert updated is not None
            assert updated.state == 'mood_captured'
            assert updated.mood_score == 4
            
            # Update to next state
            updated = update_check_in_state(
                active_check_in.id,
                'stress_captured',
                mood_description='Feeling good today'
            )
            
            assert updated is not None
            assert updated.state == 'stress_captured'
            assert updated.mood_description == 'Feeling good today'
            
            # Update to completed state
            updated = update_check_in_state(
                active_check_in.id,
                'completed',
                stress_level=3,
                stress_factors='Work deadlines',
                qualitative_feedback='Overall fine'
            )
            
            assert updated is not None
            assert updated.state == 'completed'
            assert updated.is_completed is True
            assert updated.stress_level == 3
            assert updated.completed_at is not None
    
    def test_handle_check_in_response_initial(self, app, test_user):
        """Test handling initial check-in request"""
        with app.app_context():
            # Clean up any existing check-ins
            CheckIn.query.filter_by(user_id=test_user.id).delete()
            db.session.commit()
            
            # Test initiating a check-in
            result = handle_check_in_response(test_user.id, 'start check-in')
            
            assert result['response_text'] == RESPONSES['initiate']
            assert result['check_in'] is not None
            assert result['check_in'].state == 'initiated'
            
            # Test non-check-in message
            result = handle_check_in_response(test_user.id, 'just chatting')
            assert result['response_text'] is None
    
    def test_handle_check_in_flow(self, app, test_user, active_check_in):
        """Test the full check-in flow"""
        with app.app_context():
            # Reset check-in state
            active_check_in.state = 'initiated'
            db.session.commit()
            
            # Step 1: Rating mood
            result = handle_check_in_response(test_user.id, '4')
            assert result['response_text'] == RESPONSES['mood_followup']
            assert result['check_in'].state == 'mood_captured'
            assert result['check_in'].mood_score == 4
            
            # Step 2: Describing mood
            result = handle_check_in_response(test_user.id, 'Feeling good overall')
            assert result['response_text'] == RESPONSES['stress_question']
            assert result['check_in'].state == 'stress_captured'
            assert result['check_in'].mood_description == 'Feeling good overall'
            
            # Step 3: Rating stress
            result = handle_check_in_response(test_user.id, '3')
            assert result['response_text'] == RESPONSES['stress_followup']
            assert result['check_in'].state == 'feedback_captured'
            assert result['check_in'].stress_level == 3
            
            # Step 4: Describing stress factors
            result = handle_check_in_response(test_user.id, 'Some project deadlines')
            assert result['response_text'] == RESPONSES['qualitative_feedback']
            assert result['check_in'].state == 'qualitative_feedback'
            assert result['check_in'].stress_factors == 'Some project deadlines'
            
            # Step 5: Providing qualitative feedback
            result = handle_check_in_response(test_user.id, 'Overall a good week')
            assert result['response_text'] == RESPONSES['completion']
            assert result['check_in'].state == 'completed'
            assert result['check_in'].qualitative_feedback == 'Overall a good week'
            assert result['check_in'].is_completed is True
    
    def test_handle_invalid_responses(self, app, test_user, active_check_in):
        """Test handling invalid responses during check-in"""
        with app.app_context():
            # Reset check-in state
            active_check_in.state = 'initiated'
            db.session.commit()
            
            # Test invalid mood rating
            result = handle_check_in_response(test_user.id, 'good')
            assert "didn't understand" in result['response_text'].lower()
            assert result['check_in'].state == 'initiated'
            
            # Test out of range mood rating
            result = handle_check_in_response(test_user.id, '7')
            assert "between 1 and 5" in result['response_text'].lower()
            assert result['check_in'].state == 'initiated'
            
            # Set state to stress_captured for testing stress rating
            active_check_in.state = 'stress_captured'
            db.session.commit()
            
            # Test invalid stress rating
            result = handle_check_in_response(test_user.id, 'medium')
            assert "didn't understand" in result['response_text'].lower()
            assert result['check_in'].state == 'stress_captured'
    
    def test_timeout_handling(self, app, test_user):
        """Test handling of check-in timeouts"""
        with app.app_context():
            # Create a check-in that's about to expire
            expiring_check_in = CheckIn(
                user_id=test_user.id,
                state='mood_captured',
                is_completed=False,
                last_interaction_time=datetime.utcnow() - timedelta(minutes=29),
                expires_at=datetime.utcnow() + timedelta(minutes=1)
            )
            db.session.add(expiring_check_in)
            
            # Create a check-in that's already expired
            expired_check_in = CheckIn(
                user_id=test_user.id,
                state='initiated',
                is_completed=False,
                is_expired=False,
                last_interaction_time=datetime.utcnow() - timedelta(minutes=35),
                expires_at=datetime.utcnow() - timedelta(minutes=5)
            )
            db.session.add(expired_check_in)
            db.session.commit()
            
            # Test that timeout is detected
            result = handle_check_in_response(test_user.id, 'hello')
            assert result['response_text'] == RESPONSES['timeout']
            assert expired_check_in.is_expired is True
            
            # Test that a new check-in can be started after timeout
            result = handle_check_in_response(test_user.id, 'start check-in')
            assert result['response_text'] == RESPONSES['initiate']
            assert result['check_in'] is not None
            assert result['check_in'].id != expired_check_in.id
    
    def test_handle_timeout_checks(self, app, test_user):
        """Test the timeout check function"""
        with app.app_context():
            # Clean up existing check-ins
            CheckIn.query.filter_by(user_id=test_user.id).delete()
            db.session.commit()
            
            # Create check-ins with different timeout states
            # 1. Normal active check-in
            active = CheckIn(
                user_id=test_user.id,
                state='initiated',
                is_completed=False,
                is_expired=False,
                last_interaction_time=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=30)
            )
            
            # 2. Warning threshold check-in (25 min old)
            warning = CheckIn(
                user_id=test_user.id,
                state='mood_captured',
                is_completed=False,
                is_expired=False,
                last_interaction_time=datetime.utcnow() - timedelta(minutes=26),
                expires_at=datetime.utcnow() + timedelta(minutes=4)
            )
            
            # 3. Expired check-in (35 min old)
            expired = CheckIn(
                user_id=test_user.id,
                state='stress_captured',
                is_completed=False,
                is_expired=False,
                last_interaction_time=datetime.utcnow() - timedelta(minutes=35),
                expires_at=datetime.utcnow() - timedelta(minutes=5)
            )
            
            db.session.add_all([active, warning, expired])
            db.session.commit()
            
            # Run timeout check
            result = handle_timeout_checks()
            
            # Verify results
            assert result['warnings'] == 1
            assert result['expirations'] == 1
            
            # Refresh check-ins from database
            db.session.refresh(active)
            db.session.refresh(warning)
            db.session.refresh(expired)
            
            # Verify states
            assert active.is_expired is False
            assert warning.is_expired is False
            assert expired.is_expired is True 