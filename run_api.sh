#!/bin/bash

echo "🐍 Starting Basilisk API Server..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Run the API server
cd api
python server.py
