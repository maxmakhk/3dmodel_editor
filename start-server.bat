@echo off
REM GLB Texture Editor - Python Server Launcher (Windows)
REM 
REM Usage: 
REM   start-server.bat              (use default port 3000)
REM   start-server.bat 8080         (use custom port)

cd /d "%~dp0"

set PORT=3000
if not "%~1"=="" set "PORT=%~1"

echo ===================================================
echo   GLB Texture Editor Server Launcher
echo ===================================================

rem Default to python
set PYTHON_CMD=python

rem Check if python is working
%PYTHON_CMD% --version >nul 2>nul
if errorlevel 1 (
    rem Try python3
    set PYTHON_CMD=python3
    python3 --version >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python was not found in your PATH.
        echo Please install Python and check "Add Python to PATH".
        echo Then run this script again.
        echo ===================================================
        pause
        exit /b 1
    )
)

echo   Using Python command: %PYTHON_CMD%

rem Create virtual environment if it doesn't exist
if not exist .venv (
    echo   Creating Python virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [WARNING] Failed to create virtual environment.
        echo   Trying to run global Python instead...
        goto :run_global
    )
)

rem Activate virtual environment
echo   Activating virtual environment...
if not exist .venv\Scripts\activate.bat (
    echo [WARNING] virtual environment activation file not found.
    goto :run_global
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [WARNING] Failed to activate virtual environment.
    goto :run_global
)

echo   Checking dependencies inside .venv...
python -c "import flask, flask_cors" >nul 2>nul
if errorlevel 1 (
    echo   Installing required packages flask and flask-cors inside .venv...
    python -m pip install --upgrade pip
    python -m pip install flask flask-cors
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies in .venv.
        pause
        exit /b 1
    )
)

echo   Starting server on port %PORT%...
echo   Open browser: http://localhost:%PORT%
echo   Press Ctrl+C to stop the server
echo ===================================================
python server.py %PORT%
goto :end

:run_global
echo   Checking global dependencies...
%PYTHON_CMD% -c "import flask, flask_cors" >nul 2>nul
if errorlevel 1 (
    echo   Installing flask and flask-cors on global Python...
    %PYTHON_CMD% -m pip install flask flask-cors
    if errorlevel 1 (
        echo [ERROR] Failed to install flask and flask-cors.
        pause
        exit /b 1
    )
)
echo   Starting global server on port %PORT%...
%PYTHON_CMD% server.py %PORT%

:end
if errorlevel 1 (
    echo.
    echo [ERROR] Server stopped with error.
    pause
)
