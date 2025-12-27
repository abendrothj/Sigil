#!/bin/bash

echo "=================================================="
echo "🐍 Project Basilisk - Setup Script"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check Node version
echo "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Web UI will not be available."
    echo "   Install from: https://nodejs.org"
    NODE_INSTALLED=false
else
    NODE_VERSION=$(node --version)
    echo "✅ Node $NODE_VERSION found"
    NODE_INSTALLED=true
fi
echo ""

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install poison-core dependencies
echo ""
echo "Installing poison-core dependencies..."
cd poison-core
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ poison-core dependencies installed"
else
    echo "❌ Failed to install poison-core dependencies"
    exit 1
fi
cd ..

# Install API dependencies
echo ""
echo "Installing API server dependencies..."
cd api
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ API dependencies installed"
else
    echo "❌ Failed to install API dependencies"
    exit 1
fi
cd ..

# Setup Web UI if Node is installed
if [ "$NODE_INSTALLED" = true ]; then
    echo ""
    echo "Installing Web UI dependencies..."
    cd web-ui
    npm install
    if [ $? -eq 0 ]; then
        echo "✅ Web UI dependencies installed"
    else
        echo "⚠️  Failed to install Web UI dependencies"
    fi
    cd ..
fi

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Test the CLI (poison-core):"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo "   ${GREEN}python poison-core/poison_cli.py info${NC}"
echo ""
echo "2. Start the API server:"
echo "   ${GREEN}./run_api.sh${NC}"
echo ""
if [ "$NODE_INSTALLED" = true ]; then
echo "3. Start the Web UI (in another terminal):"
echo "   ${GREEN}./run_web.sh${NC}"
echo "   Then visit: http://localhost:3000"
echo ""
fi
echo "4. Run verification tests:"
echo "   ${GREEN}./run_verification.sh${NC}"
echo ""
echo "=================================================="
