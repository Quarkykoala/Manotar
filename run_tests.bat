@echo off
ECHO Running Manobal Tests with new directory structure

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    ECHO WARNING: Virtual environment not found. Using system Python.
)

:: Set environment variable for testing
SET FLASK_ENV=testing
SET TEST_DATABASE_URL=sqlite:///:memory:

:: Run all tests from the root directory
ECHO Running all tests...
pytest 

:: Run backend tests only
ECHO.
ECHO Running backend tests only...
pytest tests/backend -v

:: Run frontend tests only (when implemented)
ECHO.
ECHO Running frontend tests only...
pytest tests/frontend -v

:: Run integration tests only (when implemented)
ECHO.
ECHO Running integration tests only...
pytest tests/integration -v

ECHO.
ECHO All tests completed.

:: Deactivate virtual environment if it was activated
if exist venv\Scripts\activate.bat (
    call venv\Scripts\deactivate.bat
) 