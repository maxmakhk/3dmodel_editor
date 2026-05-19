#!/bin/bash
# GLB Texture Editor - Node.js Server Launcher (Linux/macOS)
# 
# Usage: 
#   ./start-server.sh              (use default port 3000)
#   ./start-server.sh 8080         (use custom port)
#
# Make executable: chmod +x start-server.sh

PORT=${1:-3000}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  GLB Texture Editor Server                                 ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Checking Node.js..."

if ! command -v node &> /dev/null; then
    echo "║  ❌ Node.js not found!                                      ║"
    echo "║                                                            ║"
    echo "║  Please install Node.js:                                  ║"
    echo "║  • macOS: brew install node                               ║"
    echo "║  • Linux: apt install nodejs npm (Debian/Ubuntu)          ║"
    echo "║  • Or: https://nodejs.org/                                ║"
    echo "║                                                            ║"
    echo "║  Then run this script again.                              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

NODE_VER=$(node --version)
echo "║  ✓ Node.js $NODE_VER found"
echo "║                                                            ║"
echo "║  Starting server on port $PORT...                          "
echo "║  🌐 Open browser: http://localhost:$PORT                 "
echo "║  📁 Save file: glb-save.json                              ║"
echo "║  Press Ctrl+C to stop server                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

node server.js $PORT

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "❌ Error starting server (exit code: $exit_code)"
    exit $exit_code
fi
