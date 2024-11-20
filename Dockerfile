FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages with verbose output for debugging
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy application code
COPY . .

# Download NLTK data with error handling
RUN python -c "import nltk; nltk.download('punkt', quiet=False); nltk.download('stopwords', quiet=False)" || exit 1

# Environment variables will be set through DigitalOcean's interface
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app", "--timeout", "120"] 