@echo off
REM Nivora Extension Build Script (Windows)
REM =======================================

echo 🔧 Building Nivora Browser Extension...
echo ======================================

REM Navigate to extension directory
cd nivora-extension
if %ERRORLEVEL% neq 0 (
    echo ❌ Extension directory not found
    pause
    exit /b 1
)

echo 📦 Installing dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo 🔨 Building extension...
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo.
echo ✅ Extension built successfully!
echo.
echo 📋 Installation Instructions:
echo 1. Open Chrome and go to chrome://extensions/
echo 2. Enable 'Developer mode' ^(top right toggle^)
echo 3. Click 'Load unpacked'
echo 4. Select the 'dist' folder in this directory:
echo    %cd%\dist
echo.
echo 🔧 Important Files:
echo - Manifest: %cd%\dist\manifest.json
echo - Main HTML: %cd%\dist\index.html
echo - Assets: %cd%\dist\assets\
echo.
echo 🎯 Usage:
echo - Click the extension icon in the toolbar
echo - Or press Alt+N to open quickly
echo - Make sure the token server and agent are running!
echo.
pause