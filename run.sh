#!/bin/bash
set -e

echo "========================================================"
echo "   Plant Disease Information Agent - Setup & Launch"
echo "========================================================"
echo ""

# Check python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+."
    exit 1
fi

# Create virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Install dependencies
echo "Installing dependencies..."
.venv/bin/pip install -r requirements.txt

# Launch server
echo ""
echo "Starting Plant Disease Agent on http://localhost:8000 ..."

# Attempt to open browser automatically
if command -v xdg-open &> /dev/null; then
    (sleep 1 && xdg-open http://localhost:8000) &
elif command -v open &> /dev/null; then
    (sleep 1 && open http://localhost:8000) &
fi

.venv/bin/python3 backend/main.py
