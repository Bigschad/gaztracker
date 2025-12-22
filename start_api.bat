@echo off
REM GazTracker API - Startup Script
REM Run this file to start the API server

echo ================================
echo    GAZTRACKER API SERVER
echo ================================
echo.

REM Check if in correct directory
if not exist "app\main.py" (
    echo ERROR: Please run this script from the project root directory
    pause
    exit /b 1
)

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo.

echo [2/3] Checking Database Connection...
REM Add database check here if needed
echo Database check skipped (add psql check if needed)
echo.

echo [3/3] Starting API Server...
echo.
echo API will be available at:
echo   - http://localhost:8000
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo Press CTRL+C to stop the server
echo.
echo ================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

