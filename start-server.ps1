# GLB Texture Editor - Python Server Launcher (PowerShell)
# 
# Usage: 
#   .\start-server.ps1              (use default port 3000)
#   .\start-server.ps1 -Port 8080   (use custom port)

param(
    [int]$Port = 3000
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommandPath
Set-Location $scriptDir

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  GLB Texture Editor Server Launcher" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Checking Python..." -ForegroundColor Cyan

$pythonCmd = "python"
$pythonCheck = python --version 2>$null
if ($null -eq $pythonCheck) {
    $pythonCheck = python3 --version 2>$null
    if ($null -eq $pythonCheck) {
        Write-Host "[ERROR] Python not found!" -ForegroundColor Red
        Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Yellow
        Write-Host "Then run this script again." -ForegroundColor Yellow
        Write-Host "===================================================" -ForegroundColor Cyan
        Read-Host "Press Enter to exit"
        exit 1
    } else {
        $pythonCmd = "python3"
    }
}

Write-Host "  Found $pythonCheck" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path ".venv")) {
    Write-Host "  Creating Python virtual environment (.venv)..." -ForegroundColor Cyan
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] Failed to create virtual environment." -ForegroundColor Yellow
        Write-Host "Trying to run global Python instead..." -ForegroundColor Yellow
        goto run_global
    }
}

# Activate virtual environment
Write-Host "  Activating virtual environment..." -ForegroundColor Cyan
if ($IsWindows) {
    .venv\Scripts\Activate.ps1
} else {
    .venv/bin/Activate.ps1
}

# Check dependencies
Write-Host "  Checking dependencies..." -ForegroundColor Cyan
python -c "import flask, flask_cors" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing required packages (flask, flask-cors) in .venv..." -ForegroundColor Cyan
    python -m pip install --upgrade pip
    python -m pip install flask flask-cors
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "  Starting server on port $Port..." -ForegroundColor Green
Write-Host "  Open browser: http://localhost:$Port" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
python server.py $Port
exit

:run_global
Write-Host "  Checking global dependencies..." -ForegroundColor Cyan
& $pythonCmd -c "import flask, flask_cors" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing flask and flask-cors on global Python..." -ForegroundColor Cyan
    & $pythonCmd -m pip install flask flask-cors
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install flask and flask-cors." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host "  Starting global server on port $Port..." -ForegroundColor Green
& $pythonCmd server.py $Port
