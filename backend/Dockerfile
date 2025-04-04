FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create NLTK data directory and download required data
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt stopwords

# Copy application code
COPY . .

# Environment variables will be set through deployment platform interface
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run using the entrypoint script
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app", "--timeout", "120"] 