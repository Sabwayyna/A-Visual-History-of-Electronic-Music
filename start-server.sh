#!/bin/bash
# Simple script to start a local server for the music visualizer

echo "Starting local server..."
echo "Open your browser and go to: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    python -m http.server 8000
else
    echo "Error: Python not found. Please install Python to run a local server."
    exit 1
fi

