@echo off
echo Starting comprehensive project cleanup...

:: Set project root directory
set PROJECT_ROOT=%CD%

echo Cleaning up project structure...

:: Remove unnecessary directories
rmdir /s /q src\styles 2>nul
rmdir /s /q src\components\CreditCardForm* 2>nul
rmdir /s /q src\assets\scss 2>nul
rmdir /s /q src\themes 2>nul
rmdir /s /q .husky 2>nul
rmdir /s /q .github 2>nul
rmdir /s /q berry-free-react-admin-template 2>nul
rmdir /s /q remix 2>nul
rmdir /s /q vite 2>nul
rmdir /s /q __pycache__ 2>nul
rmdir /s /q .pytest_cache 2>nul
rmdir /s /q .coverage 2>nul
rmdir /s /q htmlcov 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q *.egg-info 2>nul

:: Remove unnecessary files
del /f /q .yarnrc 2>nul
del /f /q .npmrc 2>nul
del /f /q .nvmrc 2>nul
del /f /q .stylelintrc 2>nul
del /f /q .prettierrc.js 2>nul
del /f /q .eslintrc.js 2>nul
del /f /q CODE_OF_CONDUCT.md 2>nul
del /f /q CONTRIBUTING.md 2>nul
del /f /q SECURITY.md 2>nul
del /f /q yarn.lock 2>nul
del /f /q package-lock.json 2>nul
del /f /q .DS_Store 2>nul
del /f /q *.log 2>nul
del /f /q *.bak 2>nul
del /f /q *.swp 2>nul
del /s /q *.pyc 2>nul

:: Clean frontend
cd frontend
rmdir /s /q node_modules 2>nul
call npm cache clean --force

:: Create essential structure
mkdir src\layout\MainLayout 2>nul
mkdir src\pages\Dashboard 2>nul
mkdir src\pages\Analytics 2>nul
mkdir public 2>nul

:: Create minimal package.json if it doesn't exist
if not exist package.json (
    echo { "name": "mental-health-dashboard", "version": "1.0.0", "private": true } > package.json
)

cd ..

:: Clean up redundant cleanup scripts
del /f /q cleanup_frontend.bat 2>nul
del /f /q frontend_cleanup.bat 2>nul
del /f /q project_cleanup.bat 2>nul
del /f /q create_test_structure.bat 2>nul

echo Cleanup complete! Project structure has been optimized.
pause
