"""
Sentiment Analysis Service

This module provides sentiment analysis capabilities using the Hume API.
It analyzes text messages and returns sentiment scores.
"""

import os
import logging
import httpx
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from flask import current_app

# Configure logging
logger = logging.getLogger(__name__)

class HumeSentimentAnalyzer:
    """
    Sentiment analysis using Hume API
    
    This class provides methods to analyze text sentiment using Hume's
    emotion recognition API.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Hume Sentiment Analyzer
        
        Args:
            api_key: Hume API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('HUME_API_KEY')
        if not self.api_key:
            logger.warning("No Hume API key provided. Sentiment analysis will not work.")
        
        self.api_url = "https://api.hume.ai/v0/batch/jobs"
        self.models = ["language"]
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of text using Hume API
        
        Args:
            text: The text to analyze
            
        Returns:
            Dict containing sentiment analysis results
        """
        if not self.api_key:
            logger.error("No Hume API key available. Cannot perform sentiment analysis.")
            return self._generate_fallback_sentiment()
        
        try:
            logger.info(f"Analyzing sentiment for text: {text[:50]}...")
            
            # Prepare the request payload
            payload = {
                "models": {
                    "language": {}
                },
                "data": {
                    "text": text
                }
            }
            
            headers = {
                "X-Hume-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Send request to Hume API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                
                # Check response status
                if response.status_code != 200:
                    logger.error(f"Hume API returned error: {response.status_code}, {response.text}")
                    return self._generate_fallback_sentiment()
                
                # Process the response
                response_data = response.json()
                job_id = response_data.get("job_id")
                
                if not job_id:
                    logger.error("No job_id in Hume API response")
                    return self._generate_fallback_sentiment()
                
                # Poll for results
                result = await self._poll_for_results(client, job_id, headers)
                return self._process_results(result)
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return self._generate_fallback_sentiment()
    
    async def _poll_for_results(self, client: httpx.AsyncClient, job_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Poll the Hume API for analysis results"""
        status_url = f"{self.api_url}/{job_id}"
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            response = await client.get(status_url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Error polling Hume API: {response.status_code}, {response.text}")
                await asyncio.sleep(2)
                continue
            
            data = response.json()
            status = data.get("state")
            
            if status == "completed":
                return data.get("results", {})
            elif status == "failed":
                logger.error(f"Hume API job failed: {data.get('error', 'Unknown error')}")
                break
            
            # Wait before polling again
            await asyncio.sleep(2)
        
        logger.error(f"Timed out waiting for Hume API results after {max_attempts} attempts")
        return {}
    
    def _process_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize Hume API results"""
        try:
            # Extract language model predictions
            language_predictions = results.get('language', {}).get('predictions', [])
            
            if not language_predictions:
                return self._generate_fallback_sentiment()
            
            # Extract emotions data
            emotions = language_predictions[0].get('emotions', [])
            
            # Calculate weighted sentiment score
            # Positive emotions: joy, amusement, admiration, approval, gratitude, excitement, love
            # Negative emotions: grief, anger, fear, disgust, disappointment, embarrassment, regret
            # Normalize to 0.0 - 1.0 range
            
            positive_emotions = ['joy', 'amusement', 'admiration', 'approval', 'gratitude', 'excitement', 'love']
            negative_emotions = ['grief', 'anger', 'fear', 'disgust', 'disappointment', 'embarrassment', 'regret']
            
            emotion_dict = {e['name']: e['score'] for e in emotions}
            
            positive_score = sum(emotion_dict.get(e, 0) for e in positive_emotions)
            negative_score = sum(emotion_dict.get(e, 0) for e in negative_emotions)
            
            # Calculate normalized sentiment score (0 to 1)
            total = positive_score + negative_score
            if total > 0:
                sentiment_score = positive_score / total
            else:
                sentiment_score = 0.5  # Neutral if no signal
            
            # Return structured result
            return {
                'sentiment_score': sentiment_score,
                'emotions': emotion_dict,
                'positive_score': positive_score,
                'negative_score': negative_score,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'hume_api'
            }
            
        except Exception as e:
            logger.error(f"Error processing Hume API results: {str(e)}")
            return self._generate_fallback_sentiment()
    
    def _generate_fallback_sentiment(self) -> Dict[str, Any]:
        """Generate fallback sentiment when API fails"""
        return {
            'sentiment_score': 0.5,  # Neutral score
            'emotions': {},
            'positive_score': 0,
            'negative_score': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'fallback'
        }

# Synchronous wrapper function for easier integration
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze text sentiment (synchronous wrapper)
    
    Args:
        text: The text to analyze
        
    Returns:
        Dict containing sentiment analysis results
    """
    analyzer = HumeSentimentAnalyzer()
    
    # Use asyncio to run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(analyzer.analyze_text(text))
        return result
    finally:
        loop.close()

# Function to extract key emotions with scores
def extract_key_emotions(sentiment_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Extract the top emotions from sentiment analysis data
    
    Args:
        sentiment_data: The sentiment analysis result
        limit: Maximum number of emotions to return
        
    Returns:
        List of top emotions with their scores
    """
    emotions = sentiment_data.get('emotions', {})
    
    # Sort emotions by score in descending order
    sorted_emotions = sorted(
        [{'name': name, 'score': score} for name, score in emotions.items()],
        key=lambda x: x['score'],
        reverse=True
    )
    
    # Return top N emotions
    return sorted_emotions[:limit]

# Function to categorize sentiment
def categorize_sentiment(sentiment_score: float) -> str:
    """
    Categorize a sentiment score into a textual category
    
    Args:
        sentiment_score: Sentiment score (0.0 to 1.0)
        
    Returns:
        Sentiment category string
    """
    if sentiment_score >= 0.75:
        return "very_positive"
    elif sentiment_score >= 0.6:
        return "positive"
    elif sentiment_score >= 0.4:
        return "neutral"
    elif sentiment_score >= 0.25:
        return "negative"
    else:
        return "very_negative" 