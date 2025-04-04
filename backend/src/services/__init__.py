"""
Services package for Manobal Platform

This package contains service modules that provide core functionality
for the application, such as sentiment analysis and external API integration.
"""

from .sentiment_analysis import analyze_sentiment, extract_key_emotions, categorize_sentiment
from .async_worker import init_async_worker, queue_sentiment_analysis
