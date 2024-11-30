@echo off
echo Creating test directory structure...

:: Create main directories
mkdir logs 2>nul
mkdir frontend\logs 2>nul
mkdir frontend\src\tests 2>nul
mkdir frontend\src\utils 2>nul
mkdir frontend\scripts 2>nul
mkdir tests 2>nul

:: Create test files
echo. > tests\__init__.py
echo. > tests\test_api.py
echo. > tests\init_test_db.py

:: Create frontend test files
echo. > frontend\src\tests\App.test.tsx
echo. > frontend\src\tests\Dashboard.test.tsx

:: Create utility files
copy /Y NUL frontend\src\utils\errorTracker.ts
copy /Y NUL frontend\src\utils\testLogger.ts
copy /Y NUL frontend\scripts\generateErrorReport.js

echo Directory structure created successfully! 