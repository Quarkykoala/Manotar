@echo off
echo Installing frontend dependencies...

cd frontend

:: Install core dependencies
call npm install react@18.2.0 react-dom@18.2.0 typescript@4.9.5
call npm install @types/react@18.2.0 @types/react-dom@18.2.0
call npm install react-scripts@5.0.1 web-vitals@2.1.4

:: Install UI dependencies
call npm install @mui/material@5.14.5 @emotion/react@11.11.1 @emotion/styled@11.11.0
call npm install @mui/icons-material@5.14.5

:: Install routing and data fetching
call npm install react-router-dom@6.15.0 axios@1.4.0

:: Install chart libraries
call npm install chart.js@4.3.3 react-chartjs-2@5.2.0

:: Install dev dependencies
call npm install --save-dev @babel/plugin-proposal-private-property-in-object@7.21.11
call npm install --save-dev ajv@8.12.0

echo Installation complete!
pause
