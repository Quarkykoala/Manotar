@echo off
echo Updating Node.js to latest LTS version

:: Check if nvm is installed
where nvm >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Node Version Manager (nvm)
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/coreybutler/nvm-windows/releases/download/1.1.11/nvm-setup.exe' -OutFile 'nvm-setup.exe'}"
    start /wait nvm-setup.exe
    del nvm-setup.exe
    
    :: Update PATH
    setx PATH "%PATH%;%APPDATA%\nvm"
    
    :: Refresh environment
    call refreshenv
)

:: Install Node.js 18 LTS
echo Installing Node.js 18 LTS
call nvm install 18.17.1
call nvm use 18.17.1

:: Verify installation
echo Verifying Node.js version
node --version
npm --version

:: Clear npm cache
echo Cleaning npm cache
call npm cache clean --force

:: Remove existing node_modules
if exist "frontend\node_modules" (
    echo Removing old node_modules
    rmdir /s /q frontend\node_modules
)

:: Remove package-lock.json
if exist "frontend\package-lock.json" (
    echo Removing package-lock.json
    del /f /q frontend\package-lock.json
)

:: Reinstall dependencies
echo Reinstalling dependencies
cd frontend
call npm install

echo Node.js update complete!
pause