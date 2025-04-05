"""
Tests for the Check-in Flow Service

This module contains tests for the check_in_flow service which manages
the structured check-in conversation with employees.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from backend.src.services.check_in_flow import (
    get_active_check_in,
    create_check_in, 
    update_check_in_state,
    handle_check_in_response,
    handle_timeout_checks,
    get_check_in_statistics,
    CHECK_IN_TIMEOUT,
    RESPONSES
)
from backend.src.models.models import CheckIn, User, Employee, db


class TestCheckInFlow:
    """Test suite for the Check-in Flow service."""

    def test_get_active_check_in_with_existing_session(self, app, db_session, test_user):
        """Test retrieving an active check-in session."""
        # Create an active check-in
        check_in = CheckIn(
            user_id=test_user.id,
            state='initiated',
            is_completed=False,
            is_expired=False,
            last_interaction_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + CHECK_IN_TIMEOUT
        )
        db_session.add(check_in)
        db_session.commit()

        # Test retrieval
        active_check_in = get_active_check_in(test_user.id)
        assert active_check_in is not None
        assert active_check_in.id == check_in.id
        assert active_check_in.user_id == test_user.id
        assert active_check_in.state == 'initiated'
        assert not active_check_in.is_completed
        assert not active_check_in.is_expired

    def test_get_active_check_in_no_session(self, app, db_session, test_user):
        """Test retrieving when no active check-in exists."""
        active_check_in = get_active_check_in(test_user.id)
        assert active_check_in is None

    def test_get_active_check_in_completed_session(self, app, db_session, test_user):
        """Test that completed sessions are not returned."""
        # Create a completed check-in
        check_in = CheckIn(
            user_id=test_user.id,
            state='completed',
            is_completed=True,
            is_expired=False,
            last_interaction_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + CHECK_IN_TIMEOUT
        )
        db_session.add(check_in)
        db_session.commit()

        active_check_in = get_active_check_in(test_user.id)
        assert active_check_in is None

    def test_create_check_in(self, app, db_session, test_user, test_employee):
        """Test creating a new check-in session."""
        check_in = create_check_in(test_user.id)
        
        assert check_in is not None
        assert check_in.user_id == test_user.id
        assert check_in.employee_id == test_employee.id
        assert check_in.state == 'initiated'
        assert not check_in.is_completed
        assert not check_in.is_expired
        assert check_in.last_interaction_time is not None
        assert check_in.expires_at > datetime.utcnow()

    def test_create_check_in_no_employee(self, app, db_session, test_user):
        """Test creating a check-in for a user without an associated employee."""
        # Remove any associated employee
        Employee.query.filter_by(user_id=test_user.id).delete()
        db_session.commit()
        
        check_in = create_check_in(test_user.id)
        
        assert check_in is not None
        assert check_in.user_id == test_user.id
        assert check_in.employee_id is None
        assert check_in.state == 'initiated'

    def test_update_check_in_state(self, app, db_session, test_user):
        """Test updating the state of a check-in."""
        # Create a check-in first
        check_in = CheckIn(
            user_id=test_user.id,
            state='initiated',
            is_completed=False,
            is_expired=False,
            last_interaction_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + CHECK_IN_TIMEOUT
        )
        db_session.add(check_in)
        db_session.commit()
        
        # Update the state
        updated_check_in = update_check_in_state(
            check_in.id, 
            'mood_captured',
            mood_score=4
        )
        
        assert updated_check_in is not None
        assert updated_check_in.state == 'mood_captured'
        assert updated_check_in.mood_score == 4
        assert updated_check_in.last_interaction_time > check_in.last_interaction_time
        assert updated_check_in.expires_at > check_in.expires_at

    def test_update_check_in_state_to_completed(self, app, db_session, test_user):
        """Test updating a check-in to completed state."""
        # Create a check-in
        check_in = CheckIn(
            user_id=test_user.id,
            state='feedback_captured',
            is_completed=False,
            is_expired=False,
            last_interaction_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + CHECK_IN_TIMEOUT
        )
        db_session.add(check_in)
        db_session.commit()
        
        # Update to completed
        updated_check_in = update_check_in_state(check_in.id, 'completed')
        
        assert updated_check_in is not None
        assert updated_check_in.state == 'completed'
        assert updated_check_in.is_completed
        assert updated_check_in.completed_at is not None

    def test_update_nonexistent_check_in(self, app, db_session):
        """Test updating a check-in that doesn't exist."""
        result = update_check_in_state(999999, 'mood_captured')
        assert result is None

    def test_handle_check_in_response_start_new(self, app, db_session, test_user):
        """Test handling a request to start a new check-in."""
        response = handle_check_in_response(test_user.id, "start check-in")
        
        assert response['response_text'] == RESPONSES['initiate']
        assert response['check_in'] is not None
        assert response['check_in'].state == 'initiated'

    def test_handle_check_in_response_unrelated_message(self, app, db_session, test_user):
        """Test handling a message unrelated to check-ins."""
        response = handle_check_in_response(test_user.id, "hello there")
        
        assert response['response_text'] is None
        assert response['check_in'] is None

    @patch('backend.src.services.check_in_flow.datetime')
    def test_handle_check_in_response_expired_session(self, mock_datetime, app, db_session, test_user):
        """Test handling a response to an expired session."""
        # Mock current time to be after expiration
        current_time = datetime.utcnow()
        expired_time = current_time - timedelta(minutes=10)
        mock_datetime.utcnow.return_value = current_time
        
        # Create an expired check-in
        check_in = CheckIn(
            user_id=test_user.id,
            state='initiated',
            is_completed=False,
            is_expired=False,
            last_interaction_time=expired_time,
            expires_at=expired_time + timedelta(minutes=5)  # Expired 5 minutes ago
        )
        db_session.add(check_in)
        db_session.commit()
        
        response = handle_check_in_response(test_user.id, "4")
        
        assert response['response_text'] == RESPONSES['timeout']
        assert response['check_in'] is None
        
        # Check that the original check-in was marked as expired
        updated_check_in = CheckIn.query.get(check_in.id)
        assert updated_check_in.is_expired

    def test_handle_check_in_mood_rating(self, app, db_session, test_user):
        """Test handling a mood rating response."""
        # Create an active check-in
        check_in = CheckIn(
            user_id=test_user.id,
            state='initiated',
            is_completed=False,
            is_expired=False,
            last_interaction_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + CHECK_IN_TIMEOUT
        )
        db_session.add(check_in)
        db_session.commit()
        
        response = handle_check_in_response(test_user.id, "4")
        
        assert response['response_text'] == RESPONSES['mood_followup']
        assert response['check_in'].state == 'mood_captured'
        assert response['check_in'].mood_score == 4

    @patch('backend.src.services.check_in_flow.datetime')
    def test_handle_timeout_checks(self, mock_datetime, app, db_session, test_user):
        """Test the timeout check functionality."""
        current_time = datetime.utcnow()
        almost_expired = current_time - timedelta(minutes=25)  # 25 minutes ago
        expired_time = current_time - timedelta(minutes=35)  # 35 minutes ago
        mock_datetime.utcnow.return_value = current_time
        
        # Create an almost expired check-in
        almost_expired_check_in = CheckIn(
            user_id=test_user.id,
            state='initiated',
            is_completed=False,
            is_expired=False,
            last_interaction_time=almost_expired,
            expires_at=almost_expired + CHECK_IN_TIMEOUT
        )
        
        # Create an expired check-in
        expired_check_in = CheckIn(
            user_id=999,  # Different user
            state='mood_captured',
            is_completed=False,
            is_expired=False,
            last_interaction_time=expired_time,
            expires_at=expired_time + CHECK_IN_TIMEOUT
        )
        
        db_session.add(almost_expired_check_in)
        db_session.add(expired_check_in)
        db_session.commit()
        
        timeout_results = handle_timeout_checks()
        
        # The expired check-in should now be marked as expired
        updated_expired = CheckIn.query.get(expired_check_in.id)
        assert updated_expired.is_expired
        
        # The almost expired check-in should have a warning sent
        assert test_user.id in timeout_results['warnings']
        assert 999 in timeout_results['timeouts']

    def test_get_check_in_statistics(self, app, db_session, test_user, test_employee):
        """Test retrieving check-in statistics."""
        # Create completed check-ins with various moods and stress levels
        for mood, stress in [(5, 2), (4, 3), (3, 3), (2, 4)]:
            check_in = CheckIn(
                user_id=test_user.id,
                employee_id=test_employee.id,
                state='completed',
                is_completed=True,
                is_expired=False,
                mood_score=mood,
                stress_score=stress,
                last_interaction_time=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db_session.add(check_in)
        db_session.commit()
        
        stats = get_check_in_statistics()
        
        assert stats['total_check_ins'] == 4
        assert stats['average_mood'] == 3.5  # (5+4+3+2)/4
        assert stats['average_stress'] == 3.0  # (2+3+3+4)/4
        assert stats['completion_rate'] == 100.0  # All are completed
        
        # Test filtering by department
        dept_stats = get_check_in_statistics(department=test_employee.department)
        assert dept_stats['total_check_ins'] == 4  # All belong to the same department
        
        # Test filtering by date range
        last_week = datetime.utcnow() - timedelta(days=7)
        date_stats = get_check_in_statistics(start_date=last_week)
        assert date_stats['total_check_ins'] == 4  # All created now 