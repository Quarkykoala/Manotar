@echo off
echo Cleaning up frontend...

:: Remove node_modules and package-lock.json
cd frontend
rmdir /s /q node_modules
del /f /q package-lock.json

:: Clean npm cache
call npm cache clean --force

echo Cleanup complete!
pause
