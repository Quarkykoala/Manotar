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

# Create instance directory for SQLite (if used)
RUN mkdir -p instance

# Run migrations
RUN python run_sql_migrations.py

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 5000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"] 