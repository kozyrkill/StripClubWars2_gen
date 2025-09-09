#!/usr/bin/env bash
# Installer script for SCW Image Generator in a virtual environment

echo "Installing dependencies for SCW Character Image Pack Generator..."

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 not found. Please install Python 3.8 or newer."
    exit 1
fi

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
fi

# Activate venv and install deps
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
if python -m pip install -r requirements.txt; then
    echo "✓ Dependencies installed successfully in the virtual environment!"
    echo "To run the generator:"
    echo "1. Activate the virtual env:"
    echo "   source venv/bin/activate"
    echo "2. Ensure Stable Diffusion WebUI is running with --api"
    echo "3. Generate: python scw_image_generator.py --test"
    echo "Or use activate.sh for a quick activation"
else
    echo "✗ Dependency installation failed"
    exit 1
fi
