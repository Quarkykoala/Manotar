# Manobal - Mental Health Platform

Manobal is an AI-powered mental health platform designed to provide emotional support and wellness monitoring for employees. It combines a WhatsApp-based chatbot with an analytics dashboard for HR professionals to monitor organizational sentiment anonymously.

## Project Structure

This project follows a monorepo structure with separate directories for backend and frontend:

```
manobal/
├── backend/           # Flask API, models, services
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
- MySQL/PostgreSQL database (or SQLite for development)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Quarkykoala/Manotar.git
   cd Manotar
   ```

2. **Set up the backend**
   ```bash
   # Create a Python virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r backend/requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Setup the database
   python -m scripts.init_db
   
   # Run the Flask application
   python backend/run.py
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
   - Backend API: http://localhost:5000
   - Frontend Dashboard: http://localhost:3000

## Development

### Running Tests

```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
# Generate a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
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

This application handles sensitive mental health data and complies with GDPR requirements. All data is anonymized and users have the right to request data deletion. 