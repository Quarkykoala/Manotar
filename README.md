# Manobal - Mental Health Platform

Manobal is an AI-powered mental health platform designed to provide emotional support and wellness monitoring for employees. It combines a WhatsApp-based chatbot with an analytics dashboard for HR professionals to monitor organizational sentiment anonymously.

## Project Structure

This project follows a monorepo structure with separate directories for backend and frontend:

```
manobal/
├── backend/           # Flask API, models, services
│   ├── src/
│   │   ├── api/       # API endpoints (versioned)
│   │   ├── models/    # Database models
│   │   └── services/  # Business logic services
├── frontend/          # Next.js web application 
├── shared/            # Shared types and utilities
├── docs/              # Project documentation
├── scripts/           # Utility scripts
├── tests/             # Test files
└── migrations/        # Database migration scripts
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- SQLite (development) or PostgreSQL (production)
- Hume API key for sentiment analysis
- Twilio account for WhatsApp integration
- Google AI API key for Gemini models

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Quarkykoala/Manotar.git
   cd Manotar
   ```

2. **Set up the backend**
   ```bash
   cd backend
   
   # On Linux/macOS:
   ./setup.sh
   
   # On Windows (PowerShell):
   .\setup.ps1
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration:
   # - HUME_API_KEY
   # - TWILIO_ACCOUNT_SID
   # - TWILIO_AUTH_TOKEN
   # - GOOGLE_API_KEY
   
   # Run the Flask application
   flask run
   ```

3. **Set up the frontend**
   ```bash
   # Navigate to the frontend directory
   cd frontend
   
   # Install dependencies
   npm install
   
   # Run the development server
   npm run dev
   ```

4. **Access the application**
   - Backend API: http://localhost:5000/api/v1
   - Frontend Dashboard: http://localhost:3000

## API Structure

The API follows a versioned structure:

```
/api/v1/
  ├── auth/           # Authentication endpoints
  ├── bot/            # WhatsApp bot webhook
  ├── dashboard/      # HR dashboard data endpoints
  ├── employees/      # Employee management
  └── admin/          # Admin-only operations
```

## Key Features

### Sentiment Analysis

The platform uses the Hume API to analyze the sentiment of user messages. The sentiment analysis service:

- Processes text to extract emotions and sentiment scores
- Categorizes sentiment into 5 levels (very negative to very positive)
- Extracts key emotions for reporting
- Handles API failures with graceful fallbacks
- Processes sentiment asynchronously to avoid webhook timeouts

### WhatsApp Bot

The WhatsApp bot provides:
- Conversational mental health support using Gemini AI
- User authentication and consent management
- Message logging with sentiment analysis
- Daily check-ins and reminders

### HR Dashboard

The dashboard offers:
- Department-level sentiment analysis
- Time-series trends of employee wellbeing
- Keyword statistics to identify common concerns
- Anonymized reporting to protect employee privacy

## Development

### Utility Scripts

The project includes various utility scripts organized in the `scripts/` directory:

```
scripts/
├── backend/   # Backend setup and operations
├── db/        # Database initialization and management
├── deploy/    # Deployment and maintenance
├── frontend/  # Frontend application scripts
├── setup/     # Project setup and configuration
└── test/      # Testing utilities
```

For detailed information about available scripts, refer to the [scripts README](scripts/README.md).

### Running Tests

The project uses a unified test structure organized by domain:

```
tests/
├── backend/     # Backend API, models, services tests
├── frontend/    # Frontend component, page, hook tests
├── integration/ # Tests that span frontend-backend boundary
└── fixtures/    # Test data and fixtures shared across tests
```

To run all tests:

```bash
# Run all tests from the project root
pytest

# Or use the test script
scripts/test/run_tests.bat
```

To run specific test categories:

```bash
# Backend tests only
pytest tests/backend

# Frontend tests only
pytest tests/frontend

# Integration tests only
pytest tests/integration
```

For more details, see the [testing documentation](tests/README.md).

### Database Migrations

```bash
# Apply migrations
cd backend
python run_sql_migrations.py

# Or use the database scripts
scripts/db/init_db.py  # For fresh setup
```

## Deployment

See the [deployment documentation](docs/setup/deployment.md) for detailed instructions on deploying to production environments.

## Documentation

- [API Documentation](docs/api/v1.md)
- [Architecture](docs/architecture/README.md)
- [Setup Guides](docs/setup/README.md)
- [User Guides](docs/user-guides/README.md)

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Security and Privacy

This application handles sensitive mental health data and complies with GDPR requirements:
- All data is anonymized in dashboard views
- Users have the right to request data deletion (within 30 days)
- Data retention period is limited to 24 months
- Secure authentication and role-based access control
- All API endpoints are protected with appropriate authorization checks 

### Environment Variables

The project uses a standardized approach to environment variables:

```
project/
├── .env.example     # Template with placeholders (committed)
├── .env             # Local development values (not committed)
├── .env.test        # Test environment values (not committed)
├── .env.production  # Production values (not committed)
├── backend/
│   ├── .env.example # Backend-specific template
│   └── .env         # Backend-specific values
└── frontend/
    ├── .env.example # Frontend-specific template
    └── .env         # Frontend-specific values
```

To set up environment variables for a new environment:

```bash
# For Windows (PowerShell)
./scripts/setup/setup_env.ps1 [environment]

# For Linux/macOS
./scripts/setup/setup_env.sh [environment]
```

To verify environment file configuration:

```bash
# For Windows (PowerShell)
./scripts/deploy/env_cleanup.ps1

# For Linux/macOS
./scripts/deploy/env_cleanup.sh
```

For detailed information, see the [Environment Variable Strategy](docs/setup/environment.md).

### Handling Sensitive Files

For security reasons, sensitive files such as API keys and service account credentials are **never** committed to the repository. 

- All sensitive credentials should be stored in the `.env` file (which is ignored by Git)
- Service account keys should be placed in the `secrets/` directory, which is excluded from Git
- When setting up a new environment, request the necessary credentials from an administrator
- Reference credentials only through environment variables, never hardcode them

Example of proper credential handling in code:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

# Access credentials safely
api_key = os.environ.get("HUME_API_KEY")
```

If you accidentally commit sensitive information, follow these steps:
1. Immediately remove the file from Git using `git rm --cached <file>`
2. Commit this removal
3. Move the file to the `secrets/` directory
4. Update `.gitignore` to prevent future occurrences
5. Contact an administrator as the credentials may need to be rotated 