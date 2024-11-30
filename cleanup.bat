@echo off
echo Cleaning up unnecessary files...

:: Remove unnecessary directories
rmdir /s /q src\styles 2>nul
rmdir /s /q src\components\CreditCardForm* 2>nul
rmdir /s /q scripts 2>nul
rmdir /s /q src\assets\scss 2>nul
rmdir /s /q src\themes 2>nul
rmdir /s /q src\utils 2>nul
rmdir /s /q .husky 2>nul
rmdir /s /q .github 2>nul

:: Remove unnecessary files
del /f /q .yarnrc 2>nul
del /f /q .npmrc 2>nul
del /f /q .nvmrc 2>nul
del /f /q tsconfig.json 2>nul
del /f /q tsconfig.paths.json 2>nul
del /f /q .stylelintrc 2>nul
del /f /q .prettierrc.js 2>nul
del /f /q .eslintrc.js 2>nul
del /f /q CODE_OF_CONDUCT.md 2>nul
del /f /q CONTRIBUTING.md 2>nul
del /f /q SECURITY.md 2>nul
del /f /q yarn.lock 2>nul
del /f /q package-lock.json 2>nul

echo Cleanup complete!

:: Create essential directories
mkdir src\layout\MainLayout 2>nul
mkdir src\pages\Dashboard 2>nul
mkdir src\pages\Analytics 2>nul
mkdir public 2>nul

echo Essential directories created!
