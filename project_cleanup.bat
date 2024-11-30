@echo off
echo Starting project cleanup...

:: Set the project root directory
set PROJECT_ROOT=C:\Users\hp\Desktop\Mental Health bot

:: Navigate to project directory
cd "%PROJECT_ROOT%"

echo Cleaning up frontend directory...

:: Remove frontend directory completely
rmdir /s /q frontend 2>nul

:: Create fresh directories
mkdir frontend
cd frontend

:: Create essential structure
mkdir src\layout\MainLayout
mkdir src\pages\Dashboard
mkdir src\pages\Analytics
mkdir public

:: Create essential files
echo { "name": "mental-health-dashboard", "version": "1.0.0", "private": true } > package.json

:: Keep only necessary backend files
cd "%PROJECT_ROOT%"
echo Cleaning up unnecessary backend files...

:: Remove cache and compiled files
del /s /q *.pyc 2>nul
rmdir /s /q __pycache__ 2>nul
rmdir /s /q .pytest_cache 2>nul
rmdir /s /q .coverage 2>nul
rmdir /s /q htmlcov 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q *.egg-info 2>nul

:: Remove development files
del /f /q .DS_Store 2>nul
del /f /q *.log 2>nul
del /f /q *.bak 2>nul
del /f /q *.swp 2>nul

echo Cleanup complete!
echo.
echo Project structure has been cleaned and reorganized.
echo Ready to start fresh!
pause
