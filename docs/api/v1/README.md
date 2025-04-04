# Manobal API v1 Documentation

This document describes the v1 API endpoints for the Manobal mental health platform.

## API Base URL

All API endpoints are prefixed with: `/api/v1/`

## Authentication

Most API endpoints require authentication using JWT tokens. To authenticate:

1. Get a token from the `/api/v1/auth/login` endpoint
2. Include the token in the `Authorization` header of subsequent requests:
   ```
   Authorization: Bearer <token>
   ```

## Error Handling

All API endpoints return consistent error responses in the following format:

```json
{
  "success": false,
  "error": {
    "id": "unique-error-id",
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if available
    },
    "status": 400 // HTTP status code
  }
}
```

Common error codes:
- `BAD_REQUEST`: The request was malformed or missing required parameters
- `UNAUTHORIZED`: Authentication is required or the provided token is invalid
- `FORBIDDEN`: The authenticated user does not have permission to access the resource
- `NOT_FOUND`: The requested resource does not exist
- `SERVER_ERROR`: An internal server error occurred

## Dashboard API

### Dashboard Overview

GET `/api/v1/dashboard/dashboard`

Returns overall dashboard data with sentiment scores and department/location counts.

**Auth required**: Yes (HR or Admin)

**Response**:
```json
{
  "success": true,
  "data": {
    "overall_sentiment": 0.75,
    "department_counts": {
      "Engineering": 25,
      "Marketing": 10,
      "HR": 5
    },
    "location_counts": {
      "Remote": 20,
      "New York": 15,
      "London": 5
    },
    "total_users": 40,
    "active_users_last_week": 30
  }
}
```

### Department Comparison

GET `/api/v1/dashboard/department-comparison`

Provides department comparison data for sentiment analysis.

**Auth required**: Yes (HR or Admin)

**Query parameters**:
- `start_date` (optional): Start date for filtering data (ISO format)
- `end_date` (optional): End date for filtering data (ISO format)

**Response**:
```json
{
  "success": true,
  "data": {
    "departments": [
      {
        "name": "Engineering",
        "sentiment_score": 0.72,
        "user_count": 25,
        "message_count": 150
      },
      {
        "name": "Marketing",
        "sentiment_score": 0.81,
        "user_count": 10,
        "message_count": 75
      }
    ]
  }
}
```

### Time Series Data

GET `/api/v1/dashboard/time-series`

Returns time series data for sentiment trends.

**Auth required**: Yes (HR or Admin)

**Query parameters**:
- `department` (optional): Filter by department
- `location` (optional): Filter by location
- `start_date` (optional): Start date for filtering data (ISO format)
- `end_date` (optional): End date for filtering data (ISO format)
- `interval` (optional): Grouping interval - 'day', 'week', or 'month' (default: 'day')

**Response**:
```json
{
  "success": true,
  "data": {
    "interval": "day",
    "points": [
      {
        "date": "2023-01-01T00:00:00Z",
        "sentiment_score": 0.68,
        "message_count": 42
      },
      {
        "date": "2023-01-02T00:00:00Z",
        "sentiment_score": 0.72,
        "message_count": 37
      }
    ]
  }
}
```

### Department Details

GET `/api/v1/dashboard/department/{department}/details`

Retrieves detailed information for a specific department.

**Auth required**: Yes (HR or Admin)

**URL parameters**:
- `department`: The department name

**Response**:
```json
{
  "success": true,
  "data": {
    "department": "Engineering",
    "user_count": 25,
    "sentiment_score": 0.72,
    "top_keywords": [
      {"keyword": "project", "count": 52},
      {"keyword": "deadline", "count": 38},
      {"keyword": "meeting", "count": 27}
    ],
    "sentiment_trend": [
      {"date": "2023-01-01", "score": 0.68},
      {"date": "2023-01-02", "score": 0.72}
    ]
  }
}
```

### Keyword Statistics

GET `/api/v1/dashboard/keyword-stats`

Provides keyword statistics across all departments.

**Auth required**: Yes (HR or Admin)

**Query parameters**:
- `department` (optional): Filter by department
- `location` (optional): Filter by location
- `start_date` (optional): Start date for filtering data (ISO format)
- `end_date` (optional): End date for filtering data (ISO format)
- `limit` (optional): Maximum number of keywords to return (default: 20)

**Response**:
```json
{
  "success": true,
  "data": {
    "keywords": [
      {"keyword": "project", "count": 127, "departments": ["Engineering", "Marketing"]},
      {"keyword": "deadline", "count": 98, "departments": ["Engineering", "HR"]},
      {"keyword": "meeting", "count": 87, "departments": ["Engineering", "Marketing", "HR"]}
    ]
  }
}
```

## Bot API

### Webhook Endpoint

POST `/api/v1/bot/bot`

Webhook endpoint for WhatsApp messages via Twilio.

**Auth required**: No (Twilio webhook authentication handled separately)

**Request**:
```
Body: Message content
From: whatsapp:+1234567890
To: whatsapp:+0987654321
```

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "message": "Response sent"
  }
}
```

## Authentication API

### Login

POST `/api/v1/auth/login`

Login endpoint for dashboard users.

**Auth required**: No

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "token": "jwt-token-here",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "User Name",
      "role": "hr"
    }
  }
}
```

### Register User

POST `/api/v1/auth/register`

Register a new HR or admin user.

**Auth required**: Yes (Admin only)

**Request**:
```json
{
  "email": "newuser@example.com",
  "name": "New User",
  "password": "password123",
  "role": "hr"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "user": {
      "id": 2,
      "email": "newuser@example.com",
      "name": "New User",
      "role": "hr"
    }
  }
}
```

### Verify Token

GET `/api/v1/auth/verify-token`

Verify if the current token is valid.

**Auth required**: Yes

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "User Name",
      "role": "hr"
    }
  }
}
```

### Reset Password

POST `/api/v1/auth/reset-password`

Reset a user's password.

**Auth required**: Yes

**Request**:
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "message": "Password reset successfully"
  }
}
```

### Get Users

GET `/api/v1/auth/users`

Get a list of all users.

**Auth required**: Yes (Admin only)

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "users": [
      {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "role": "admin",
        "created_at": "2023-01-01T00:00:00Z",
        "last_login": "2023-01-02T00:00:00Z"
      },
      {
        "id": 2,
        "email": "newuser@example.com",
        "name": "New User",
        "role": "hr",
        "created_at": "2023-01-03T00:00:00Z",
        "last_login": null
      }
    ]
  }
}
```

### Delete User

DELETE `/api/v1/auth/users/{user_id}`

Delete a user.

**Auth required**: Yes (Admin only)

**URL parameters**:
- `user_id`: The ID of the user to delete

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "message": "User 2 deleted successfully"
  }
}
``` 