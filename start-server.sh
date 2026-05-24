#!/bin/bash
# GLB Texture Editor - Python Server Launcher (Linux/macOS)
# 
# Usage: 
#   ./start-server.sh              (use default port 3000)
#   ./start-server.sh 8080         (use custom port)
#
# Make executable: chmod +x start-server.sh

PORT=${1:-3000}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "==================================================="
echo "  GLB Texture Editor Server Launcher"
echo "==================================================="
echo "  Checking Python..."

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python not found!"
    echo "Please install Python."
    echo "==================================================="
    exit 1
fi

PYTHON_VER=$($PYTHON_CMD --version)
echo "  Found $PYTHON_VER"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "  Creating Python virtual environment (.venv)..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[WARNING] Failed to create virtual environment."
        echo "Trying to run global Python instead..."
        # Fallback to global
        PYTHON_EXEC=$PYTHON_CMD
    fi
fi

if [ -f ".venv/bin/activate" ]; then
    echo "  Activating virtual environment..."
    source .venv/bin/activate
    PYTHON_EXEC="python"
else
    PYTHON_EXEC=$PYTHON_CMD
fi

echo "  Checking dependencies..."
$PYTHON_EXEC -c "import flask, flask_cors" &> /dev/null
if [ $? -ne 0 ]; then
    echo "  Installing required packages (flask, flask-cors) in .venv..."
    $PYTHON_EXEC -m pip install --upgrade pip
    $PYTHON_EXEC -m pip install flask flask-cors
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies."
        exit 1
    fi
fi

echo "  Starting server on port $PORT..."
echo "  Open browser: http://localhost:$PORT"
echo "  Press Ctrl+C to stop the server"
echo "==================================================="
$PYTHON_EXEC server.py $PORT
