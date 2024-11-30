@echo off
echo Testing Frontend Setup...
echo ============================

:: Navigate to frontend directory
cd frontend

:: Clean install dependencies
echo Installing dependencies...
call npm ci

:: Run tests
echo Running tests...
call npm test

:: Start development server
echo Starting development server...
call npm start

pause
