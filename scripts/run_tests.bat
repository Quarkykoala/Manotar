@echo off
echo Running Backend Tests...

:: Set Python path to include the project root
set PYTHONPATH=%PYTHONPATH%;%CD%

:: Initialize test database
cd tests
python init_test_db.py

:: Run Python tests
python -m unittest test_api.py -v

echo.
echo Running Frontend Tests...

:: Run Frontend tests
cd ..\frontend
call npm test -- --watchAll=false

pause 