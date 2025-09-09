#!/usr/bin/env bash
# Quick activation script for the virtual environment

if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Run: bash setup.sh"
    exit 1
fi

source venv/bin/activate

echo "🟢 Virtual environment activated!"
echo "Available commands:"
echo "  python scw_image_generator.py --test             - generate samples"
echo "  python scw_image_generator.py --config character_config.json  - generate from config"
echo "To deactivate: deactivate"

# Start a new shell with venv activated
$SHELL
