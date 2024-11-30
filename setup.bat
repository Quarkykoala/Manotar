@echo off
echo Starting Mental Health Bot Setup...
echo ============================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python first.
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed! Please install Node.js first.
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install Python dependencies
echo Installing Python dependencies...
pip install flask flask-sqlalchemy flask-migrate flask-login flask-cors
pip install python-dotenv twilio google-generativeai nltk requests
pip install werkzeug

:: Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

:: Initialize the database
echo Initializing database...
python init_db.py
flask db init
flask db migrate -m "initial migration"
flask db upgrade

:: Create frontend if it doesn't exist
if not exist "frontend" (
    echo Setting up React frontend...
    npx create-react-app frontend --template typescript
)

:: Install frontend dependencies
cd frontend
echo Installing frontend dependencies...
call npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
call npm install react-router-dom @types/react-router-dom
call npm install chart.js react-chartjs-2
call npm install axios

:: Create necessary directories
echo Creating project structure...
mkdir src\components\Layout 2>nul
mkdir src\pages\Dashboard 2>nul
mkdir src\pages\Analytics 2>nul
mkdir src\services 2>nul

cd ..

:: Create a start script
echo @echo off > start.bat
echo echo Starting Mental Health Bot... >> start.bat
echo echo Starting Backend Server... >> start.bat
echo start cmd /k "call venv\Scripts\activate && python app.py" >> start.bat
echo timeout /t 5 >> start.bat
echo echo Starting Frontend Development Server... >> start.bat
echo start cmd /k "cd frontend && npm start" >> start.bat

echo Setup complete!
echo To start the application, run 'start.bat'
echo ============================

pause
