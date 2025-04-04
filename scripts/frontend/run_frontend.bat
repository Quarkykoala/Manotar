@echo off
echo Starting Frontend Setup and Run...

:: Check if node_modules exists
if not exist "frontend\node_modules" (
    echo Installing dependencies...
    cd frontend
    
    :: Install dependencies
    call npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
    call npm install react-router-dom @types/react-router-dom
    call npm install chart.js react-chartjs-2
    call npm install axios framer-motion lucide-react
    call npm install --save-dev @babel/plugin-proposal-private-property-in-object
    call npm install @tailwindcss/forms tailwindcss postcss autoprefixer
    
    :: Initialize Tailwind CSS
    call npx tailwindcss init -p
    
    cd ..
)

:: Create hooks directory if it doesn't exist
if not exist "frontend\src\hooks" (
    mkdir "frontend\src\hooks"
)

:: Start the frontend
cd frontend
npm start

pause
