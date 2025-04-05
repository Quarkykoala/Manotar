"""
Check-in Flow Service

This module handles the structured check-in flow, managing conversation state,
prompts, and transitions between different stages of the check-in process.
"""

from datetime import datetime, timedelta
from flask import current_app
from ..models.models import CheckIn, User, Employee, db

# Constants
CHECK_IN_TIMEOUT = timedelta(minutes=30)  # Session expires after 30 minutes of inactivity
CHECK_IN_STATES = [
    'initiated',
    'mood_captured',
    'stress_captured',
    'feedback_captured',
    'completed'
]

# Response templates for different check-in steps
RESPONSES = {
    'initiate': (
        "Let's start a quick check-in to see how you're doing today. "
        "On a scale of 1-5, how would you rate your mood today? "
        "(1 being very low, 5 being excellent)"
    ),
    'mood_followup': (
        "Thank you. Could you share a few words about why you're feeling that way today?"
    ),
    'stress_question': (
        "Now, on a scale of 1-5, how would you rate your stress level today? "
        "(1 being very relaxed, 5 being extremely stressed)"
    ),
    'stress_followup': (
        "Thank you. Could you briefly mention what factors are contributing to your stress level?"
    ),
    'qualitative_feedback': (
        "Last question: Is there anything specific you'd like to share about your work experience or well-being lately?"
    ),
    'completion': (
        "Thank you for completing today's check-in. Your responses help us understand how to better support you. "
        "Your check-in has been recorded and if needed, appropriate support resources will be provided. "
        "Feel free to reach out anytime you need to talk."
    ),
    'timeout_warning': (
        "Just a reminder that your check-in session will timeout in 5 minutes if there's no activity. "
        "Would you like to continue where we left off?"
    ),
    'timeout': (
        "Your check-in session has timed out due to inactivity. You can start a new check-in anytime "
        "by typing 'start check-in'."
    )
}

def get_active_check_in(user_id):
    """
    Retrieve the active check-in session for a user if one exists
    
    Args:
        user_id: ID of the user
        
    Returns:
        CheckIn object or None if no active session
    """
    return CheckIn.query.filter(
        CheckIn.user_id == user_id,
        CheckIn.is_completed == False,
        CheckIn.is_expired == False
    ).order_by(CheckIn.created_at.desc()).first()

def create_check_in(user_id):
    """
    Create a new check-in session for a user
    
    Args:
        user_id: ID of the user
        
    Returns:
        Newly created CheckIn object
    """
    # Try to find associated employee
    user = User.query.get(user_id)
    employee = None
    if user:
        employee = Employee.query.filter_by(user_id=user_id).first()
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + CHECK_IN_TIMEOUT
    
    # Create new check-in
    check_in = CheckIn(
        user_id=user_id,
        employee_id=employee.id if employee else None,
        state='initiated',
        is_completed=False,
        last_interaction_time=datetime.utcnow(),
        expires_at=expires_at
    )
    
    db.session.add(check_in)
    db.session.commit()
    
    return check_in

def update_check_in_state(check_in_id, new_state, **kwargs):
    """
    Update the state of a check-in session and any associated data
    
    Args:
        check_in_id: ID of the check-in to update
        new_state: The new state to set
        **kwargs: Additional fields to update
        
    Returns:
        Updated CheckIn object or None if not found
    """
    check_in = CheckIn.query.get(check_in_id)
    if not check_in:
        return None
    
    # Update state
    check_in.state = new_state
    check_in.last_interaction_time = datetime.utcnow()
    
    # Update expiration time
    check_in.expires_at = datetime.utcnow() + CHECK_IN_TIMEOUT
    
    # Update any additional fields
    for key, value in kwargs.items():
        if hasattr(check_in, key):
            setattr(check_in, key, value)
    
    # If moving to completed state, set completion timestamp
    if new_state == 'completed':
        check_in.is_completed = True
        check_in.completed_at = datetime.utcnow()
    
    db.session.commit()
    return check_in

def handle_check_in_response(user_id, message_text):
    """
    Process a user's response during a check-in and determine the next step
    
    Args:
        user_id: ID of the user
        message_text: The message text from the user
        
    Returns:
        dict with response_text and check_in object
    """
    check_in = get_active_check_in(user_id)
    
    # No active check-in, create one if user wants to start
    if not check_in:
        if 'check-in' in message_text.lower() or 'check in' in message_text.lower():
            check_in = create_check_in(user_id)
            return {
                'response_text': RESPONSES['initiate'],
                'check_in': check_in
            }
        else:
            # Not related to check-in, let regular bot flow handle it
            return {
                'response_text': None,
                'check_in': None
            }
    
    # Check for timeout
    if check_in.expires_at and datetime.utcnow() > check_in.expires_at:
        # Mark check-in as expired
        check_in.is_expired = True
        db.session.commit()
        
        # Create a new check-in if the user explicitly asks
        if 'check-in' in message_text.lower() or 'check in' in message_text.lower():
            check_in = create_check_in(user_id)
            return {
                'response_text': RESPONSES['initiate'],
                'check_in': check_in
            }
        else:
            return {
                'response_text': RESPONSES['timeout'],
                'check_in': None
            }
    
    # Handle response based on current state
    if check_in.state == 'initiated':
        # Expecting mood rating (1-5)
        try:
            mood_score = int(message_text.strip())
            if 1 <= mood_score <= 5:
                check_in = update_check_in_state(
                    check_in.id, 
                    'mood_captured',
                    mood_score=mood_score
                )
                return {
                    'response_text': RESPONSES['mood_followup'],
                    'check_in': check_in
                }
            else:
                return {
                    'response_text': "Please provide a number between 1 and 5 for your mood rating.",
                    'check_in': check_in
                }
        except ValueError:
            return {
                'response_text': "I didn't understand that. Please rate your mood on a scale of 1-5.",
                'check_in': check_in
            }
    
    elif check_in.state == 'mood_captured':
        # Capturing mood description
        check_in = update_check_in_state(
            check_in.id, 
            'stress_captured',
            mood_description=message_text
        )
        return {
            'response_text': RESPONSES['stress_question'],
            'check_in': check_in
        }
    
    elif check_in.state == 'stress_captured':
        # Expecting stress rating (1-5)
        try:
            stress_level = int(message_text.strip())
            if 1 <= stress_level <= 5:
                check_in = update_check_in_state(
                    check_in.id, 
                    'feedback_captured',
                    stress_level=stress_level
                )
                return {
                    'response_text': RESPONSES['stress_followup'],
                    'check_in': check_in
                }
            else:
                return {
                    'response_text': "Please provide a number between 1 and 5 for your stress level.",
                    'check_in': check_in
                }
        except ValueError:
            return {
                'response_text': "I didn't understand that. Please rate your stress level on a scale of 1-5.",
                'check_in': check_in
            }
    
    elif check_in.state == 'feedback_captured':
        # Capturing stress factors
        check_in = update_check_in_state(
            check_in.id, 
            'qualitative_feedback',
            stress_factors=message_text
        )
        return {
            'response_text': RESPONSES['qualitative_feedback'],
            'check_in': check_in
        }
    
    elif check_in.state == 'qualitative_feedback':
        # Completing check-in
        check_in = update_check_in_state(
            check_in.id, 
            'completed',
            qualitative_feedback=message_text,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        
        # Here we would typically trigger sentiment analysis on the complete check-in
        # and possibly generate recommendations based on the responses
        # This could be done asynchronously
        
        return {
            'response_text': RESPONSES['completion'],
            'check_in': check_in
        }
    
    # Fallback
    return {
        'response_text': "I'm not sure what to do with that response. Let's continue with your check-in.",
        'check_in': check_in
    }

def handle_timeout_checks():
    """
    Process all active check-ins and handle timeouts
    
    This should be called periodically, e.g., by a scheduled task.
    """
    warning_threshold = datetime.utcnow() - timedelta(minutes=25)  # 5 min before timeout
    timeout_threshold = datetime.utcnow() - timedelta(minutes=30)  # Complete timeout
    
    # Find check-ins that should receive a warning
    warning_check_ins = CheckIn.query.filter(
        CheckIn.is_completed == False,
        CheckIn.is_expired == False,
        CheckIn.last_interaction_time <= warning_threshold,
        CheckIn.last_interaction_time > timeout_threshold
    ).all()
    
    # Find check-ins that have timed out
    expired_check_ins = CheckIn.query.filter(
        CheckIn.is_completed == False,
        CheckIn.is_expired == False,
        CheckIn.last_interaction_time <= timeout_threshold
    ).all()
    
    # Mark expired check-ins
    for check_in in expired_check_ins:
        check_in.is_expired = True
    
    db.session.commit()
    
    return {
        'warnings': len(warning_check_ins),
        'expirations': len(expired_check_ins)
    }

def get_check_in_statistics(department=None, start_date=None, end_date=None):
    """
    Get statistics on check-ins for reporting
    
    Args:
        department: Filter by department (optional)
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
        
    Returns:
        Dict containing statistics on check-ins
    """
    query = CheckIn.query.filter(CheckIn.is_completed == True)
    
    if department:
        query = query.join(Employee).filter(Employee.department == department)
    
    if start_date:
        query = query.filter(CheckIn.created_at >= start_date)
    
    if end_date:
        query = query.filter(CheckIn.created_at <= end_date)
    
    # Get all completed check-ins within criteria
    check_ins = query.all()
    
    # Calculate averages and distribution
    mood_scores = [c.mood_score for c in check_ins if c.mood_score]
    stress_levels = [c.stress_level for c in check_ins if c.stress_level]
    
    # Prepare results
    stats = {
        'total_check_ins': len(check_ins),
        'avg_mood': sum(mood_scores) / len(mood_scores) if mood_scores else 0,
        'avg_stress': sum(stress_levels) / len(stress_levels) if stress_levels else 0,
        'mood_distribution': {i: mood_scores.count(i) for i in range(1, 6)},
        'stress_distribution': {i: stress_levels.count(i) for i in range(1, 6)},
        'department': department,
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None
    }
    
    return stats 