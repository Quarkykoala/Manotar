@echo off
echo Setting up test environment...

:: Create test directories if they don't exist
if not exist "tests" mkdir tests
if not exist "frontend\src\tests" mkdir "frontend\src\tests"

:: Copy necessary files to tests directory
copy app.py tests\
copy models.py tests\
copy config.py tests\

:: Create __init__.py for Python tests
echo. > tests\__init__.py

:: Initialize test database
cd tests
python init_test_db.py
cd ..

echo Test environment setup complete!
pause 