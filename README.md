# Manotar - Mental Health Analytics Platform

Manotar is an AI-powered mental health analytics platform designed to help organizations monitor and support employee wellbeing through sentiment analysis and structured check-ins.

## Project Structure

This project follows a monorepo structure:

- `backend/`: Flask API, models, services, and Twilio webhook
- `frontend/`: Next.js app with TypeScript and TailwindCSS
- `shared/`: Types and utilities shared between frontend and backend
- `docs/`: Project documentation
- `migrations/`: Alembic database migration scripts
- `scripts/`: Utility scripts
- `tests/`: Test suite

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- MySQL or PostgreSQL database

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python init_db.py

# Run development server
flask run
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit `http://localhost:3000` to access the application.

## Testing

```bash
# Run backend tests
python -m pytest

# Run frontend tests
cd frontend
npm test
```

## Deployment

See [docs/setup/deployment.md](docs/setup/deployment.md) for detailed deployment instructions.

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is proprietary and confidential.

## Acknowledgments

- NLTK for natural language processing
- TailwindCSS for UI styling
- Twilio for WhatsApp integration 