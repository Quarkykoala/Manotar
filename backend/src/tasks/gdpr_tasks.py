"""
Scheduled tasks for GDPR compliance.

This module contains scheduled tasks that run periodically
to ensure GDPR compliance, such as data retention checks
and automated anonymization.
"""

from datetime import datetime, timedelta
from flask import current_app
from celery import shared_task
from backend.src.utils.gdpr import check_data_retention_compliance
from backend.src.models.models import db, GDPRRequest

@shared_task(name='gdpr.check_retention')
def scheduled_retention_check():
    """
    Scheduled task to check data retention compliance
    
    This task runs daily to:
    1. Check for expired data retention periods
    2. Initiate anonymization for expired data
    3. Process pending GDPR requests
    """
    with current_app.app_context():
        try:
            # Check data retention compliance
            check_data_retention_compliance()
            
            # Process overdue GDPR requests
            process_overdue_requests()
            
            current_app.logger.info("Scheduled GDPR retention check completed successfully")
            
        except Exception as e:
            current_app.logger.error(f"Error in scheduled GDPR retention check: {str(e)}")
            raise

@shared_task(name='gdpr.process_requests')
def process_pending_requests():
    """
    Process pending GDPR requests
    
    This task runs hourly to process any pending GDPR requests
    that haven't been handled manually.
    """
    with current_app.app_context():
        try:
            # Get pending requests
            pending_requests = GDPRRequest.query.filter_by(status='pending').all()
            
            for request in pending_requests:
                try:
                    process_gdpr_request(request.id)
                except Exception as e:
                    current_app.logger.error(
                        f"Error processing GDPR request {request.id}: {str(e)}"
                    )
            
            current_app.logger.info(
                f"Processed {len(pending_requests)} pending GDPR requests"
            )
            
        except Exception as e:
            current_app.logger.error(f"Error processing pending GDPR requests: {str(e)}")
            raise

def process_overdue_requests():
    """
    Process GDPR requests that are approaching their due date
    
    This function processes requests that are within 5 days of their
    due date to ensure compliance with the 30-day requirement.
    """
    try:
        # Find requests approaching due date (within 5 days)
        approaching_due = datetime.utcnow() + timedelta(days=5)
        overdue_requests = GDPRRequest.query.filter(
            GDPRRequest.status == 'pending',
            GDPRRequest.due_date <= approaching_due
        ).all()
        
        for request in overdue_requests:
            try:
                process_gdpr_request(request.id)
            except Exception as e:
                current_app.logger.error(
                    f"Error processing overdue GDPR request {request.id}: {str(e)}"
                )
        
        current_app.logger.info(
            f"Processed {len(overdue_requests)} overdue GDPR requests"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error processing overdue requests: {str(e)}")
        raise 