# Check-In API Documentation (v1)

This document provides details about the structured check-in API endpoints in version 1 of the Manobal platform.

## Base URL

All check-in API endpoints are accessible at `/api/v1/check-ins/`.

## Authentication

All check-in endpoints require authentication via JWT tokens with HR or admin privileges. To authenticate:

1. Obtain a token via the `/api/v1/auth/login` endpoint
2. Include the token in the `Authorization` header: `Authorization: Bearer <your_token>`

## Endpoints

### List Check-ins

#### `GET /api/v1/check-ins/`

Returns a paginated list of check-ins with optional filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| employee_id | Integer | Filter by employee ID |
| department | String | Filter by department |
| start_date | String | Filter by start date (YYYY-MM-DD) |
| end_date | String | Filter by end date (YYYY-MM-DD) |
| completed | Boolean | Filter by completion status (true/false) |
| follow_up_required | Boolean | Filter by follow-up flag (true/false) |
| page | Integer | Page number (default: 1) |
| per_page | Integer | Items per page (default: 20, max: 100) |

**Success Response (200 OK):**

```json
{
  "check_ins": [
    {
      "id": 1,
      "state": "completed",
      "is_completed": true,
      "mood_score": 4,
      "mood_description": "Feeling productive",
      "stress_level": 2,
      "stress_factors": "Minor deadline pressure",
      "qualitative_feedback": "Good team support this week",
      "sentiment_score": 0.75,
      "recommendations": "Continue to focus on team collaboration",
      "follow_up_required": false,
      "created_at": "2023-05-24T10:15:30.123456",
      "completed_at": "2023-05-24T10:25:45.654321",
      "is_expired": false,
      "employee": {
        "id": 42,
        "name": "Jane Smith",
        "department": "Engineering",
        "role": "Developer"
      }
    },
    // ... more check-ins
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 157,
    "pages": 8
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid parameter format
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Server error

### Get Check-in Details

#### `GET /api/v1/check-ins/{check_in_id}`

Returns detailed information about a specific check-in.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| check_in_id | Integer | ID of the check-in to retrieve |

**Success Response (200 OK):**

```json
{
  "check_in": {
    "id": 1,
    "state": "completed",
    "is_completed": true,
    "mood_score": 4,
    "mood_description": "Feeling productive",
    "stress_level": 2,
    "stress_factors": "Minor deadline pressure",
    "qualitative_feedback": "Good team support this week",
    "sentiment_score": 0.75,
    "recommendations": "Continue to focus on team collaboration",
    "follow_up_required": false,
    "follow_up_notes": null,
    "created_at": "2023-05-24T10:15:30.123456",
    "completed_at": "2023-05-24T10:25:45.654321",
    "is_expired": false,
    "employee": {
      "id": 42,
      "name": "Jane Smith",
      "department": "Engineering",
      "role": "Developer",
      "email": "jane.smith@example.com"
    }
  }
}
```

**Error Responses:**

- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Check-in not found
- `500 Internal Server Error`: Server error

### Update Follow-up Status

#### `PUT /api/v1/check-ins/{check_in_id}/follow-up`

Updates the follow-up status and notes for a check-in.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| check_in_id | Integer | ID of the check-in to update |

**Request Body:**

```json
{
  "follow_up_required": true,
  "follow_up_notes": "Schedule a call to discuss workload concerns"
}
```

**Success Response (200 OK):**

```json
{
  "message": "Check-in follow-up updated",
  "check_in": {
    "id": 1,
    "state": "completed",
    "is_completed": true,
    "follow_up_required": true,
    "follow_up_notes": "Schedule a call to discuss workload concerns",
    // ... other check-in fields
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Check-in not found
- `500 Internal Server Error`: Server error

### Get Check-in Statistics

#### `GET /api/v1/check-ins/statistics`

Returns aggregated statistics and time-series data from check-ins.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| department | String | Filter by department (optional) |
| start_date | String | Filter by start date (YYYY-MM-DD) (optional, default: 30 days ago) |
| end_date | String | Filter by end date (YYYY-MM-DD) (optional, default: today) |
| group_by | String | Group results by ('day', 'week', 'month') (default: 'day') |

**Success Response (200 OK):**

```json
{
  "total_check_ins": 157,
  "avg_mood": 3.8,
  "avg_stress": 2.4,
  "mood_distribution": {
    "1": 5,
    "2": 12,
    "3": 35,
    "4": 78,
    "5": 27
  },
  "stress_distribution": {
    "1": 18,
    "2": 45,
    "3": 62,
    "4": 25,
    "5": 7
  },
  "department": "Engineering",
  "start_date": "2023-04-24",
  "end_date": "2023-05-24",
  "time_series": [
    {
      "date": "2023-05-01",
      "avg_mood": 3.7,
      "avg_stress": 2.3,
      "check_in_count": 8
    },
    {
      "date": "2023-05-02",
      "avg_mood": 3.9,
      "avg_stress": 2.1,
      "check_in_count": 12
    }
    // ... more dates
  ],
  "group_by": "day"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid parameter format
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Server error

## Webhooks

### Check Timeouts

#### `GET /api/v1/bot/check-timeout`

Checks for timed-out check-in sessions and marks them as expired. This endpoint is designed to be called by a scheduled task to maintain conversation state.

**Success Response (200 OK):**

```json
{
  "status": "success",
  "warnings_sent": 2,
  "expired_sessions": 3
}
```

**Error Responses:**

- `500 Internal Server Error`: Server error

## Data Models

### Check-in States

The check-in flow progresses through the following states:

1. `initiated` - Check-in started, waiting for mood rating
2. `mood_captured` - Mood rating received, waiting for mood description
3. `stress_captured` - Mood description received, waiting for stress rating
4. `feedback_captured` - Stress rating received, waiting for stress description
5. `qualitative_feedback` - Stress description received, waiting for qualitative feedback
6. `completed` - Check-in completed with all information gathered

### Timeouts

Check-in sessions automatically expire after 30 minutes of inactivity.

## Data Privacy

All check-in data is treated as sensitive health information and is subject to strict access controls. Only authorized HR personnel and the employee themselves can access individual check-in data. 