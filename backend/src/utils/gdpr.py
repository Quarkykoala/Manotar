"""
GDPR compliance utilities for the Manobal API.

This module provides functions for handling GDPR-related operations
such as data anonymization, export, and deletion.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from flask import current_app
from sqlalchemy import and_
from backend.src.models.models import (
    db, User, Message, KeywordStat, SentimentLog,
    AuthUser, Employee, CheckIn, GDPRRequest
)

def anonymize_user_data(user_id: int) -> bool:
    """
    Anonymize user data while preserving statistical value
    
    Args:
        user_id: ID of the user whose data needs to be anonymized
    
    Returns:
        bool: True if anonymization was successful
    """
    try:
        user = AuthUser.query.get(user_id)
        if not user:
            return False

        # Anonymize AuthUser
        user.email = f"anonymized_{user.id}@deleted.manobal.com"
        user.name = f"Anonymized User {user.id}"
        user.is_anonymized = True
        
        # Anonymize Employee data
        employee = Employee.query.filter_by(user_id=user_id).first()
        if employee:
            employee.first_name = "Anonymized"
            employee.last_name = f"Employee {employee.id}"
            employee.email = f"anonymized_{employee.id}@deleted.manobal.com"
            employee.phone_number = None
        
        # Anonymize Messages
        messages = Message.query.filter_by(user_id=user_id).all()
        for msg in messages:
            msg.content = "[Content Removed]"
            msg.detected_keywords = None
        
        # Keep aggregated sentiment data but remove personal information
        sentiment_logs = SentimentLog.query.filter_by(user_id=user_id).all()
        for log in sentiment_logs:
            log.message_id = None
        
        db.session.commit()
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error anonymizing user data: {str(e)}")
        db.session.rollback()
        return False

def export_user_data(user_id: int) -> Dict[str, Any]:
    """
    Export all user data in a GDPR-compliant format
    
    Args:
        user_id: ID of the user whose data needs to be exported
    
    Returns:
        Dict containing all user data
    """
    user = AuthUser.query.get(user_id)
    if not user:
        return None
    
    data = {
        'personal_information': {
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        },
        'employee_information': {},
        'messages': [],
        'check_ins': [],
        'sentiment_logs': []
    }
    
    # Get employee information
    employee = Employee.query.filter_by(user_id=user_id).first()
    if employee:
        data['employee_information'] = employee.to_dict()
    
    # Get messages
    messages = Message.query.filter_by(user_id=user_id).all()
    data['messages'] = [
        {
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'is_from_user': msg.is_from_user,
            'sentiment_score': msg.sentiment_score
        } for msg in messages
    ]
    
    # Get check-ins
    check_ins = CheckIn.query.filter_by(user_id=user_id).all()
    data['check_ins'] = [check_in.to_dict() for check_in in check_ins]
    
    # Get sentiment logs
    sentiment_logs = SentimentLog.query.filter_by(user_id=user_id).all()
    data['sentiment_logs'] = [
        {
            'sentiment_score': log.sentiment_score,
            'timestamp': log.timestamp.isoformat()
        } for log in sentiment_logs
    ]
    
    return data

def delete_user_data(user_id: int) -> bool:
    """
    Permanently delete all user data
    
    Args:
        user_id: ID of the user whose data needs to be deleted
    
    Returns:
        bool: True if deletion was successful
    """
    try:
        # Delete related records first
        Message.query.filter_by(user_id=user_id).delete()
        KeywordStat.query.filter_by(user_id=user_id).delete()
        SentimentLog.query.filter_by(user_id=user_id).delete()
        CheckIn.query.filter_by(user_id=user_id).delete()
        
        # Delete employee record
        Employee.query.filter_by(user_id=user_id).delete()
        
        # Delete user record
        user = AuthUser.query.get(user_id)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error deleting user data: {str(e)}")
        db.session.rollback()
        return False

def process_gdpr_request(request_id: int) -> bool:
    """
    Process a GDPR request (export/delete/anonymize)
    
    Args:
        request_id: ID of the GDPR request to process
    
    Returns:
        bool: True if request was processed successfully
    """
    try:
        gdpr_request = GDPRRequest.query.get(request_id)
        if not gdpr_request:
            return False
        
        gdpr_request.status = 'processing'
        db.session.commit()
        
        success = False
        if gdpr_request.request_type == 'export':
            data = export_user_data(gdpr_request.user_id)
            if data:
                # Save to secure location and generate URL
                filename = f"gdpr_export_{gdpr_request.user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(current_app.config['GDPR_EXPORTS_DIR'], filename)
                with open(filepath, 'w') as f:
                    json.dump(data, f)
                gdpr_request.data_url = f"/gdpr/exports/{filename}"
                success = True
                
        elif gdpr_request.request_type == 'delete':
            success = delete_user_data(gdpr_request.user_id)
            
        elif gdpr_request.request_type == 'anonymize':
            success = anonymize_user_data(gdpr_request.user_id)
        
        gdpr_request.status = 'completed' if success else 'failed'
        gdpr_request.completed_at = datetime.utcnow()
        db.session.commit()
        
        return success
        
    except Exception as e:
        current_app.logger.error(f"Error processing GDPR request: {str(e)}")
        if gdpr_request:
            gdpr_request.status = 'failed'
            gdpr_request.notes = str(e)
            db.session.commit()
        return False

def check_data_retention_compliance():
    """
    Check and enforce data retention policies
    
    This function should be run periodically to:
    1. Identify users whose data retention period has expired
    2. Anonymize or delete their data based on policy
    """
    try:
        # Find users whose retention period has expired
        expired_users = AuthUser.query.filter(
            and_(
                AuthUser.data_retention_expiry.isnot(None),
                AuthUser.data_retention_expiry <= datetime.utcnow(),
                AuthUser.is_anonymized.is_(False)
            )
        ).all()
        
        for user in expired_users:
            # Create GDPR request for anonymization
            request = GDPRRequest(
                user_id=user.id,
                request_type='anonymize',
                status='pending',
                notes='Automated request due to retention policy expiry'
            )
            db.session.add(request)
            db.session.commit()
            
            # Process the request
            process_gdpr_request(request.id)
            
    except Exception as e:
        current_app.logger.error(f"Error in retention compliance check: {str(e)}") 