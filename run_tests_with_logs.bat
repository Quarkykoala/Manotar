@echo off
echo Running Tests with Logging...

:: Create directory structure first
call create_test_structure.bat

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs
if not exist "frontend\logs" mkdir frontend\logs

:: Generate timestamp for log file name
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=logs\test-run-%TIMESTAMP%.log
set ERROR_FILE=frontend\logs\errors-%TIMESTAMP%.json

echo Starting test run at %date% %time% > %LOG_FILE%
echo ============================== >> %LOG_FILE%

:: Run backend tests
echo Running Backend Tests... >> %LOG_FILE%
echo ------------------------------ >> %LOG_FILE%
cd tests
python -m unittest test_api.py -v >> ..\%LOG_FILE% 2>&1
cd ..

echo. >> %LOG_FILE%
echo Running Frontend Tests... >> %LOG_FILE%
echo ------------------------------ >> %LOG_FILE%

:: Run frontend tests
cd frontend
echo Installing frontend dependencies... >> ..\%LOG_FILE%
call npm install >> ..\%LOG_FILE% 2>&1

echo Running tests... >> ..\%LOG_FILE%
call npm test -- --watchAll=false --verbose >> ..\%LOG_FILE% 2>&1

:: Generate error report
echo Generating error report... >> ..\%LOG_FILE%
call npm run generate-error-report -- --output=%ERROR_FILE% >> ..\%LOG_FILE% 2>&1

:: Return to root directory
cd ..

:: Display results
echo.
echo Test Results:
echo ============================
type %LOG_FILE%
echo ============================
echo.
echo Full test logs saved to: %LOG_FILE%
echo Error report saved to: %ERROR_FILE%

:: Check for errors in log file
findstr /i "error failed" %LOG_FILE% > nul
if %errorlevel% equ 0 (
    echo.
    echo WARNING: Errors or failures detected in tests!
    echo Please check the error report for details.
    echo Error report: %ERROR_FILE%
)

pause