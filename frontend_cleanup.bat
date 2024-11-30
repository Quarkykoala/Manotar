@echo off
echo Cleaning up frontend directory...

:: Set the frontend directory
set FRONTEND_ROOT=C:\Users\hp\Desktop\Mental Health bot\frontend

:: Navigate to frontend directory
cd "%FRONTEND_ROOT%"

:: Remove template directories
rmdir /s /q berry-free-react-admin-template
rmdir /s /q remix
rmdir /s /q vite

:: Create essential structure
mkdir src\components
mkdir src\layout\MainLayout
mkdir src\pages\Dashboard
mkdir src\pages\Analytics
mkdir public

:: Create essential files
echo { "name": "mental-health-dashboard", "version": "1.0.0", "private": true } > package.json

echo Cleanup complete! Ready to set up Berry template fresh.
pause
