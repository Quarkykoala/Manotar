"""
Sample test data for fixtures.

This module contains sample data that can be used across different tests.
"""

SAMPLE_USERS = [
    {
        "phone_number": "+1234567890",
        "access_code": "ABC123XY",
        "department": "Engineering",
        "location": "Mumbai"
    },
    {
        "phone_number": "+0987654321",
        "access_code": "XYZ456AB",
        "department": "HR",
        "location": "Delhi"
    },
    {
        "phone_number": "+1122334455",
        "access_code": "MNO789PQ",
        "department": "Marketing",
        "location": "Bangalore"
    }
]

SAMPLE_KEYWORDS = ["stress", "workload", "deadline", "pressure", "anxiety"]

SAMPLE_SENTIMENT_SCORES = {
    "Engineering": 0.75,
    "HR": 0.82,
    "Marketing": 0.68,
    "Finance": 0.71
} 