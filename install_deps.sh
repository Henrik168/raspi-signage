#!/bin/bash
# Small helper to install system deps on Raspberry Pi (requires sudo)

set -euo pipefail

echo "Installing system packages (mpv, SDL libs)..."
sudo apt update
sudo apt install -y python3-venv python3-pip mpv libsdl2-2.0-0

echo "Creating virtualenv and installing python requirements..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Done. Activate the virtualenv with: source .venv/bin/activate"
