@echo off
setlocal enabledelayedexpansion

REM SAP AI Core LLM Proxy Startup Script for Windows

cd /d "%~dp0"

set "MODE=%~1"
set "CONFIG=%~2"

if "%MODE%"=="" set "MODE=dev"
if "%CONFIG%"=="" set "CONFIG=config.json"

echo SAP AI Core LLM Proxy
echo =====================
echo.

if /i "%MODE%"=="dev" (
    echo Starting in DEVELOPMENT mode...
    echo.
    echo This will start:
    echo   - Backend server on http://localhost:3001
    echo   - Frontend dev server on http://localhost:5173
    echo.
    echo Open http://localhost:5173 in your browser
    echo.

    REM Check if frontend dependencies are installed
    if not exist "frontend\node_modules" (
        echo Installing frontend dependencies...
        cd frontend
        call npm install
        cd ..
    )

    REM Start backend in new window
    echo Starting backend...
    start "SAP AI Proxy Backend" cmd /c "python proxy_server.py --config %CONFIG%"

    REM Wait for backend to start
    timeout /t 2 /nobreak > nul

    REM Start frontend dev server
    echo Starting frontend dev server...
    cd frontend
    call npm run dev
    goto :eof
)

if /i "%MODE%"=="prod" (
    echo Starting in PRODUCTION mode...
    echo.

    REM Build frontend if needed
    if not exist "static\index.html" (
        echo Building frontend...
        cd frontend
        call npm install
        call npm run build
        cd ..
    )

    echo Starting server on http://localhost:3001
    echo.
    python proxy_server.py --config %CONFIG%
    goto :eof
)

if /i "%MODE%"=="build" (
    echo Building frontend only...
    cd frontend
    call npm install
    call npm run build
    echo.
    echo Frontend built successfully to .\static\
    goto :eof
)

echo Usage: %~nx0 [dev^|prod^|build] [config.json]
echo.
echo Modes:
echo   dev   - Development mode ^(default^): Runs backend + Vite dev server
echo   prod  - Production mode: Builds frontend, runs single server
echo   build - Build frontend only
exit /b 1
