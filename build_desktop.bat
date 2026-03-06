@echo off
setlocal enabledelayedexpansion

REM ============================================
REM SAP AI Core LLM Proxy - Desktop App Builder
REM ============================================

cd /d "%~dp0"

echo.
echo ============================================
echo SAP AI Core LLM Proxy - Desktop App Builder
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Step 1: Install/Update Dependencies
echo.
echo [Step 1/5] Installing dependencies...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
    echo Continuing anyway...
)

REM Step 2: Create Icons
echo.
echo [Step 2/5] Creating application icons...
echo.
if not exist "icons\app.ico" (
    python create_icon.py
    if errorlevel 1 (
        echo WARNING: Failed to create icons
        echo The application will be built without a custom icon
    )
) else (
    echo Icons already exist, skipping...
)

REM Step 3: Build Frontend (if needed)
echo.
echo [Step 3/5] Checking frontend build...
echo.
if not exist "static\index.html" (
    echo Frontend not built, building now...
    if exist "frontend\package.json" (
        cd frontend
        
        REM Check if node_modules exists
        if not exist "node_modules" (
            echo Installing frontend dependencies...
            call npm install
        )
        
        echo Building frontend...
        call npm run build
        cd ..
        
        if not exist "static\index.html" (
            echo WARNING: Frontend build may have failed
            echo Check the frontend directory for errors
        ) else (
            echo Frontend built successfully!
        )
    ) else (
        echo WARNING: Frontend directory not found
        echo The application will run without a web interface
    )
) else (
    echo Frontend already built, skipping...
)

REM Step 4: Build with PyInstaller
echo.
echo [Step 4/5] Building desktop application with PyInstaller...
echo.

REM Clean previous builds
if exist "build" (
    echo Cleaning previous build directory...
    rmdir /s /q build
)

if exist "dist\SAP-AI-Proxy" (
    echo Cleaning previous distribution...
    rmdir /s /q "dist\SAP-AI-Proxy"
)

REM Run PyInstaller
pyinstaller sap_ai_proxy.spec --noconfirm
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Check the output above for errors.
    pause
    exit /b 1
)

REM Step 5: Copy additional files to dist
echo.
echo [Step 5/5] Finalizing distribution...
echo.

set DIST_DIR=dist\SAP-AI-Proxy

REM Copy static folder (frontend files)
if exist "static" (
    echo Copying static folder...
    xcopy /E /I /Y "static" "%DIST_DIR%\static" >nul
    echo Copied static folder
)

REM Copy icons folder
if exist "icons" (
    echo Copying icons folder...
    xcopy /E /I /Y "icons" "%DIST_DIR%\icons" >nul
    echo Copied icons folder
)

REM Copy config example
if exist "config.json.example" (
    copy "config.json.example" "%DIST_DIR%\config.json.example" >nul
    echo Copied config.json.example
)

REM Create empty logs directory
if not exist "%DIST_DIR%\logs" (
    mkdir "%DIST_DIR%\logs"
    echo Created logs directory
)

REM Create a README for the distribution
echo Creating distribution README...
(
echo SAP AI Core LLM Proxy - Desktop Application
echo ============================================
echo.
echo Quick Start:
echo -----------
echo 1. Copy config.json.example to config.json
echo 2. Edit config.json with your SAP AI Core credentials
echo 3. Double-click SAP-AI-Proxy.exe to start
echo.
echo Configuration:
echo -------------
echo - config.json: Main configuration file
echo - sap-ai-key.json: SAP AI Core service key file
echo.
echo The application will start with a graphical interface.
echo To view server logs, use the "Logs" button in the application.
echo.
echo Troubleshooting:
echo ---------------
echo - If the application doesn't start, check that config.json exists
echo - Logs are stored in the 'logs' directory
echo - For more help, see the project documentation
echo.
) > "%DIST_DIR%\README.txt"

echo.
echo ============================================
echo Build Complete!
echo ============================================
echo.
echo Distribution created at: %DIST_DIR%
echo.
echo Contents:
dir /b "%DIST_DIR%"
echo.
echo To run the application:
echo   1. Navigate to: %DIST_DIR%
echo   2. Copy your config.json and sap-ai-key.json files there
echo   3. Double-click SAP-AI-Proxy.exe
echo.
echo To distribute:
echo   - Zip the entire SAP-AI-Proxy folder
echo   - Users will need to provide their own config.json
echo.

pause