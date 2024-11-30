@echo off
echo Creating project structure...

:: Create main directories
mkdir src 2>nul
mkdir src\components 2>nul
mkdir src\components\ui 2>nul
mkdir src\pages 2>nul
mkdir src\lib 2>nul
mkdir public 2>nul

:: Create necessary files
echo Creating utility files...
echo export function cn(...classes: string[]) { return classes.filter(Boolean).join(' ') } > src\lib\utils.ts

:: Create UI components directories
mkdir src\components\ui 2>nul

echo Project structure created successfully!

:: Install dependencies
echo Installing dependencies...
call npm install

echo Setup complete! Run 'npm run dev' to start the development server.
pause
