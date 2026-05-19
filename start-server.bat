@echo off
REM GLB Texture Editor - Node.js Server Launcher (Windows)
REM 
REM Usage: 
REM   start-server.bat              (use default port 3000)
REM   start-server.bat 8080         (use custom port)

cd /d "%~dp0"

setlocal enabledelayedexpansion

if "%1"=="" (
    set PORT=3000
) else (
    set PORT=%1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  GLB Texture Editor Server                                 ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  Checking Node.js...
echo.

where node >nul 2>nul
if errorlevel 1 (
    echo ║  ❌ Node.js not found!
    echo ║                                                            ║
    echo ║  Please install Node.js from https://nodejs.org/          ║
    echo ║  Then run this script again.                              ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
echo ║  ✓ Node.js %NODE_VER% found
echo ║                                                            ║
echo ║  Starting server on port %PORT%...                          
echo ║  🌐 Open browser: http://localhost:%PORT%                 
echo ║  📁 Save file: glb-save.json                              ║
echo ║  Press Ctrl+C to stop server                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

node server.js %PORT%

if errorlevel 1 (
    echo.
    echo Error starting server. Press any key to exit...
    pause >nul
    exit /b 1
)
