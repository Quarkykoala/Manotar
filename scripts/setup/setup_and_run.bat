@echo off
echo Setting up and running frontend...

:: Navigate to frontend directory
cd "C:\Users\hp\Desktop\Mental Health bot\frontend"

:: Install dependencies if not already installed
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
    call npm install react-router-dom @types/react-router-dom
    call npm install chart.js react-chartjs-2
    call npm install axios framer-motion lucide-react
    call npm install --save-dev @babel/plugin-proposal-private-property-in-object
    call npm install @tailwindcss/forms tailwindcss postcss autoprefixer
    
    :: Initialize Tailwind CSS
    call npx tailwindcss init -p
)

:: Create hooks directory if it doesn't exist
if not exist "src\hooks" (
    mkdir "src\hooks"
)

:: Start the frontend
echo Starting frontend server...
npm start

pause
