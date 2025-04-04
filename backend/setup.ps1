# Setup script for Manobal Backend on Windows
Write-Host "Setting up Manobal Backend..."

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Initialize database
Write-Host "Initializing database..."
python run_sql_migrations.py

Write-Host "Setup complete! Run 'flask run' to start the backend server." 