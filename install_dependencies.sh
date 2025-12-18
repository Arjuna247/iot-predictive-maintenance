#!/bin/bash

# Installation script for IoT Predictive Maintenance System
# This script handles the installation of all Python dependencies

echo "============================================================"
echo "🏭 IoT Predictive Maintenance - Dependency Installer"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install Python 3.8 or higher from https://www.python.org"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed."
    echo "   Installing pip3..."
    python3 -m ensurepip --upgrade
fi

echo "✓ pip3 found: $(pip3 --version)"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
echo "   This may take a few minutes..."
echo ""

pip3 install -r requirements.txt --user

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ Installation Complete!"
    echo "============================================================"
    echo ""
    echo "📚 Next Steps:"
    echo "   1. Read SETUP_GUIDE.md for usage instructions"
    echo "   2. Start the server: cd iot && python3 esp32_data_server.py"
    echo "   3. Run simulators: cd iot && python3 client_sim.py"
    echo ""
    echo "💡 Note: Use 'python3' and 'pip3' commands on macOS"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    echo ""
    echo "Try manual installation:"
    echo "   pip3 install flask flask-cors pandas numpy scikit-learn matplotlib requests"
    echo ""
fi
