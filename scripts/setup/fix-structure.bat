@echo off
echo Fixing project structure...

:: Remove old directories if they exist
rmdir /s /q frontend 2>nul
rmdir /s /q src\styles 2>nul

:: Create fresh directory structure
mkdir src 2>nul
mkdir src\styles 2>nul
mkdir src\pages 2>nul
mkdir src\pages\dashboard 2>nul
mkdir src\components 2>nul
mkdir src\components\ui 2>nul
mkdir src\contexts 2>nul
mkdir src\hooks 2>nul
mkdir src\lib 2>nul

:: Create globals.css with proper content
echo @tailwind base;> src\styles\globals.css
echo @tailwind components;>> src\styles\globals.css
echo @tailwind utilities;>> src\styles\globals.css

:: Create utils.ts
echo export function cn(...classes: string[]) { return classes.filter(Boolean).join(' ') } > src\lib\utils.ts

echo Structure fixed! Now run:
echo npm install
echo npm run dev
pause 