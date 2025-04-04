# Manobal Architecture Overview

This document provides a high-level overview of the Manobal mental health platform architecture.

## System Components

![Architecture Diagram](../assets/architecture_diagram.png)

The Manobal platform consists of the following main components:

1. **WhatsApp Bot Interface**: A user-facing conversational interface powered by Twilio
2. **Flask Backend API**: The core application server (with versioned API endpoints)
3. **Next.js Frontend Dashboard**: An HR dashboard for monitoring organizational sentiment
4. **SQLite/PostgreSQL Database**: The data storage layer
5. **External AI Services**: Including Google Gemini and Hume API for sentiment analysis

## Data Flow

1. **User Interaction Flow**:
   - Employee initiates conversation through WhatsApp
   - Twilio webhook delivers message to Flask API
   - Message is processed by the Gemini-powered AI model
   - Response is sent back to the user via Twilio
   - Message and sentiment data are stored in the database asynchronously

2. **Analytics Flow**:
   - HR professionals log into the dashboard
   - Frontend makes API calls to the backend
   - Backend retrieves anonymized data from the database
   - Data is aggregated and sent to the frontend for visualization

## Core Services

### Sentiment Analysis Service

The sentiment analysis service uses the Hume API to analyze text and extract emotional insights:

- **Primary Emotions**: Joy, sadness, anger, fear, surprise, etc.
- **Sentiment Score**: Normalized between 0.0 (very negative) and 1.0 (very positive)
- **Async Processing**: Sentiment analysis runs in the background to avoid blocking user interactions

### Conversation Service

- Uses Gemini AI for natural language understanding and generation
- Maintains context across conversations with the same user
- Applies mental health-specific guardrails and ethical guidelines

### Dashboard Service

- Provides aggregated, anonymized sentiment data to HR
- Implements role-based access control
- Supports filtering by department, time period, and keyword

## Database Schema

The core data models include:

- **Employee**: Basic employee information (anonymized)
- **Message**: Conversation history with sentiment scores
- **SentimentLog**: Detailed sentiment analysis results
- **KeywordStat**: Extracted keywords and their frequency
- **Department**: Organizational structure information
- **User**: HR and admin user accounts for dashboard access

## Security Architecture

- **Authentication**: JWT-based authentication for API and dashboard
- **Authorization**: Role-based access control (HR vs Admin vs Bot)
- **Data Protection**: 
  - All user conversations encrypted at rest
  - Anonymized reporting to protect employee identity
  - Strict access control to sensitive data

## Scalability Considerations

- **Horizontal Scaling**: API servers can be scaled horizontally
- **Database Partitioning**: Data can be partitioned by department or time period
- **Caching Layer**: Frequently requested aggregates are cached

## Future Architectural Improvements

1. **Microservices Evolution**: Split monolithic API into specialized microservices
2. **Event-Driven Architecture**: Implement message queue for improved async processing
3. **Advanced Caching**: Implement Redis for improved performance
4. **Multi-region Deployment**: Support for global deployments with reduced latency 