# GLB Texture Editor - Node.js Server Launcher (PowerShell)
# 
# Usage: 
#   .\start-server.ps1              (use default port 3000)
#   .\start-server.ps1 -Port 8080   (use custom port)

param(
    [int]$Port = 3000
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommandPath
Set-Location $scriptDir

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  GLB Texture Editor Server                                 ║" -ForegroundColor Cyan
Write-Host "╠════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Checking Node.js..." -ForegroundColor Cyan

$nodeCheck = node --version 2>$null
if ($null -eq $nodeCheck) {
    Write-Host "║  ❌ Node.js not found!                                      ║" -ForegroundColor Red
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "║  Please install Node.js from https://nodejs.org/          ║" -ForegroundColor Cyan
    Write-Host "║  Then run this script again.                              ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "║  ✓ Node.js $nodeCheck found                                  ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "║  Starting server on port $Port...                            " -ForegroundColor Cyan
Write-Host "║  🌐 Open browser: http://localhost:$Port              " -ForegroundColor Cyan
Write-Host "║  📁 Save file: glb-save.json                              ║" -ForegroundColor Cyan
Write-Host "║  Press Ctrl+C to stop server                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

node server.js $Port

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error starting server." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit $LASTEXITCODE
}
