@echo off
echo Setting up project structure...

:: Create main directories
mkdir src 2>nul
mkdir src\styles 2>nul
mkdir src\pages 2>nul
mkdir src\components 2>nul
mkdir src\components\ui 2>nul
mkdir src\contexts 2>nul
mkdir src\hooks 2>nul
mkdir src\lib 2>nul

:: Move files to correct locations
echo Moving files to correct locations...

:: Create utils.ts
echo export function cn(...classes: string[]) { return classes.filter(Boolean).join(' ') } > src\lib\utils.ts

:: Move Dashboard component
move /Y "frontend\src\pages\Dashboard\index.tsx" "src\pages\dashboard\index.tsx" 2>nul

:: Clean up old directories
rmdir /S /Q frontend 2>nul

echo Setup complete! Running npm install...
call npm install

echo.
echo Project structure has been set up. You can now run:
echo npm run dev
pause 