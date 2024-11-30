@echo off
echo Setting up React Frontend...

:: Remove existing frontend if it exists
rmdir /s /q frontend 2>nul

:: Create new React app
npx create-react-app frontend --template typescript

:: Navigate to frontend directory
cd frontend

:: Clean install
echo Cleaning npm cache...
call npm cache clean --force

:: Install dependencies with specific versions
echo Installing dependencies...
call npm install @mui/material@5.14.5 @emotion/react@11.11.1 @emotion/styled@11.11.0 @mui/icons-material@5.14.5
call npm install react-router-dom@6.15.0 @types/react-router-dom@5.3.3
call npm install chart.js@4.3.3 react-chartjs-2@5.2.0
call npm install axios@1.4.0
call npm install --save-dev @babel/plugin-proposal-private-property-in-object@7.21.11

:: Create necessary directories
echo Creating project structure...
mkdir src\components\Layout
mkdir src\pages\Dashboard
mkdir src\pages\Analytics
mkdir src\services

:: Update package.json
echo {
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.14.5",
    "@mui/material": "^5.14.5",
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "@types/jest": "^27.5.2",
    "@types/node": "^16.18.39",
    "@types/react": "^18.2.15",
    "@types/react-dom": "^18.2.7",
    "axios": "^1.4.0",
    "chart.js": "^4.3.3",
    "react": "^18.2.0",
    "react-chartjs-2": "^5.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.15.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@babel/plugin-proposal-private-property-in-object": "^7.21.11"
  }
} > package.json

echo Frontend setup complete!
pause
