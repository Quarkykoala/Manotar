"""
Async Worker Service

This module provides asynchronous processing capabilities for tasks
that don't need to block the main request flow, like sentiment analysis.
"""

import asyncio
import logging
import threading
import queue
import time
from typing import Dict, Any, Callable, List, Optional
from flask import Flask
from datetime import datetime

from .sentiment_analysis import analyze_sentiment
from ..models.models import db, Message, SentimentLog, User

# Configure logging
logger = logging.getLogger(__name__)

# Task queue for background processing
task_queue = queue.Queue()

# Worker thread status
worker_running = False
worker_thread = None

def init_async_worker(app: Flask):
    """
    Initialize the async worker with the Flask app
    
    Args:
        app: Flask application instance
    """
    global worker_thread, worker_running
    
    if worker_running:
        logger.info("Async worker already running")
        return
    
    logger.info("Initializing async worker")
    worker_running = True
    worker_thread = threading.Thread(target=worker_loop, args=(app,), daemon=True)
    worker_thread.start()
    
    # Register shutdown handler
    @app.teardown_appcontext
    def shutdown_worker(exception=None):
        global worker_running
        worker_running = False
        logger.info("Async worker shutdown signal received")

def worker_loop(app: Flask):
    """
    Main worker loop that processes tasks from the queue
    
    Args:
        app: Flask application instance
    """
    logger.info("Async worker started")
    
    while worker_running:
        try:
            # Try to get a task from the queue (non-blocking)
            try:
                task = task_queue.get(block=True, timeout=1.0)
            except queue.Empty:
                continue
            
            # Process the task within the app context
            with app.app_context():
                logger.info(f"Processing task: {task.get('type', 'unknown')}")
                
                if task.get('type') == 'sentiment_analysis':
                    process_sentiment_analysis(task)
                elif task.get('type') == 'keyword_extraction':
                    # Could add keyword extraction later if needed
                    pass
                else:
                    logger.warning(f"Unknown task type: {task.get('type')}")
                
                # Mark task as done
                task_queue.task_done()
                
        except Exception as e:
            logger.error(f"Error in worker loop: {str(e)}")
            time.sleep(1)  # Prevent tight loop on error
    
    logger.info("Async worker stopped")

def process_sentiment_analysis(task: Dict[str, Any]):
    """
    Process a sentiment analysis task
    
    Args:
        task: Task dictionary containing message information
    """
    message_id = task.get('message_id')
    user_id = task.get('user_id')
    
    if not message_id or not user_id:
        logger.error("Missing message_id or user_id in sentiment analysis task")
        return
    
    try:
        # Get the message from the database
        message = db.session.query(Message).filter_by(id=message_id).first()
        user = db.session.query(User).filter_by(id=user_id).first()
        
        if not message:
            logger.error(f"Message not found: {message_id}")
            return
        
        if not user:
            logger.error(f"User not found: {user_id}")
            return
        
        # Analyze sentiment
        sentiment_result = analyze_sentiment(message.content)
        sentiment_score = sentiment_result.get('sentiment_score', 0.5)
        
        # Update message with sentiment score
        message.sentiment_score = sentiment_score
        
        # Create sentiment log
        sentiment_log = SentimentLog(
            user_id=user_id,
            department=user.department or "Unknown",
            location=user.location or "Unknown",
            sentiment_score=sentiment_score,
            message_id=message_id,
            timestamp=datetime.utcnow()
        )
        
        # Save to database
        db.session.add(sentiment_log)
        db.session.commit()
        
        logger.info(f"Sentiment analysis completed for message {message_id}, score: {sentiment_score:.2f}")
        
    except Exception as e:
        logger.error(f"Error processing sentiment analysis: {str(e)}")
        db.session.rollback()

def queue_sentiment_analysis(message_id: int, user_id: int):
    """
    Queue a message for sentiment analysis in the background
    
    Args:
        message_id: ID of the message to analyze
        user_id: ID of the user who sent the message
    """
    task = {
        'type': 'sentiment_analysis',
        'message_id': message_id,
        'user_id': user_id,
        'queued_at': datetime.utcnow().isoformat()
    }
    
    task_queue.put(task)
    logger.info(f"Queued sentiment analysis for message {message_id}")
    
    return True 