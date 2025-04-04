# Manobal Deployment Guide

This document provides instructions for deploying the Manobal mental health platform to various environments.

## Deployment Options

Manobal can be deployed using several different approaches:

1. **Docker Containers**: Recommended for most production environments
2. **Platform as a Service (PaaS)**: Such as Heroku or Google App Engine
3. **Virtual Machines**: Traditional deployment to cloud VMs or bare metal servers

## Prerequisites

Before deployment, ensure you have:

- API keys for required services (Twilio, Google Gemini, Hume)
- Domain name configured (for production deployments)
- SSL certificate for HTTPS (Let's Encrypt recommended)
- Database credentials (for PostgreSQL in production)

## Docker Deployment

### Building the Docker Image

1. Navigate to the project root directory
2. Build the backend Docker image:
   ```bash
   docker build -t manobal-backend:latest -f backend/Dockerfile .
   ```
3. Build the frontend Docker image:
   ```bash
   docker build -t manobal-frontend:latest -f frontend/Dockerfile .
   ```

### Environment Configuration

Create a `.env` file for each environment:

```bash
# Production environment
cp backend/.env.example backend/.env.production
# Edit backend/.env.production with production values

cp frontend/.env.example frontend/.env.production
# Edit frontend/.env.production with production values
```

### Docker Compose Deployment

1. Create a `docker-compose.yml` file in the project root:
   ```yaml
   version: '3'
   
   services:
     db:
       image: postgres:14
       volumes:
         - postgres_data:/var/lib/postgresql/data
       environment:
         - POSTGRES_PASSWORD=${DB_PASSWORD}
         - POSTGRES_USER=${DB_USER}
         - POSTGRES_DB=${DB_NAME}
       restart: always
     
     backend:
       image: manobal-backend:latest
       depends_on:
         - db
       environment:
         - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db/${DB_NAME}
         - FLASK_ENV=production
         - SECRET_KEY=${SECRET_KEY}
         - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
         - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
         - TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
         - GOOGLE_API_KEY=${GOOGLE_API_KEY}
         - HUME_API_KEY=${HUME_API_KEY}
       restart: always
       ports:
         - "5000:5000"
     
     frontend:
       image: manobal-frontend:latest
       environment:
         - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
       ports:
         - "3000:3000"
       restart: always
   
   volumes:
     postgres_data:
   ```

2. Start the services:
   ```bash
   docker-compose --env-file .env.production up -d
   ```

## Heroku Deployment

### Backend Deployment

1. Create a Heroku app:
   ```bash
   heroku create manobal-backend
   ```

2. Add PostgreSQL add-on:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. Configure environment variables:
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set TWILIO_ACCOUNT_SID=your-twilio-sid
   heroku config:set TWILIO_AUTH_TOKEN=your-twilio-token
   heroku config:set TWILIO_PHONE_NUMBER=your-twilio-number
   heroku config:set GOOGLE_API_KEY=your-google-api-key
   heroku config:set HUME_API_KEY=your-hume-api-key
   ```

4. Deploy the backend:
   ```bash
   git subtree push --prefix backend heroku main
   ```

### Frontend Deployment

1. Create a Heroku app for the frontend:
   ```bash
   heroku create manobal-frontend
   ```

2. Configure environment variables:
   ```bash
   heroku config:set NEXT_PUBLIC_API_URL=https://manobal-backend.herokuapp.com
   ```

3. Deploy the frontend:
   ```bash
   git subtree push --prefix frontend heroku-frontend main
   ```

## Google Cloud Platform Deployment

### Cloud Run Deployment

1. Build and push the Docker image to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/your-project/manobal-backend backend/
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy manobal-backend \
     --image gcr.io/your-project/manobal-backend \
     --platform managed \
     --allow-unauthenticated \
     --update-env-vars "FLASK_ENV=production,DATABASE_URL=postgresql://..."
   ```

3. Follow similar steps for the frontend deployment.

## Database Migration in Production

1. Connect to the production environment:
   ```bash
   # If using Docker:
   docker-compose exec backend bash
   
   # If using Heroku:
   heroku run bash -a manobal-backend
   ```

2. Run migration script:
   ```bash
   python run_sql_migrations.py
   ```

## SSL Configuration

For production deployments, configure SSL using:

1. **Let's Encrypt** with Certbot for direct VM deployments
2. **Cloudflare** for DNS and SSL management
3. **Heroku SSL** for Heroku deployments (requires paid plan)

## Monitoring and Logging

1. Set up logging using Sentry:
   ```python
   # Add to backend/src/app.py
   import sentry_sdk
   sentry_sdk.init(dsn="your-sentry-dsn")
   ```

2. Configure application metrics with Prometheus or Datadog.

3. Set up uptime monitoring with UptimeRobot or New Relic.

## Post-Deployment Verification

After deployment, verify:

1. The WhatsApp bot responds to messages
2. Sentiment analysis is working and storing data
3. Dashboard displays data correctly
4. User authentication works properly
5. All API endpoints return expected responses

## Backup Strategy

1. Configure regular database backups:
   - For PostgreSQL: Use `pg_dump` on a regular schedule
   - For Docker: Use volume backups
   - For Heroku: Use Heroku PG Backups add-on

2. Store backups securely with encryption and off-site storage.

## Rollback Procedure

In case of deployment issues:

1. If using Docker:
   ```bash
   docker-compose down
   docker-compose --env-file .env.production up -d --no-deps backend
   ```

2. If using Heroku:
   ```bash
   heroku rollback -a manobal-backend
   ``` 