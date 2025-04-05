"""
Task scheduling configuration for the Manobal platform.

This module configures Celery and registers scheduled tasks.
"""

from celery import Celery
from celery.schedules import crontab
from flask import current_app

def create_celery(app):
    """
    Create and configure Celery instance
    
    Args:
        app: Flask application instance
    
    Returns:
        Configured Celery instance
    """
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    # Configure Celery
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True
    )
    
    # Configure scheduled tasks
    celery.conf.beat_schedule = {
        'check-data-retention': {
            'task': 'gdpr.check_retention',
            'schedule': crontab(hour=0, minute=0)  # Run daily at midnight
        },
        'process-gdpr-requests': {
            'task': 'gdpr.process_requests',
            'schedule': crontab(minute=0)  # Run hourly
        }
    }
    
    class ContextTask(celery.Task):
        """Make Celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Import tasks after Celery is configured
from .gdpr_tasks import scheduled_retention_check, process_pending_requests 