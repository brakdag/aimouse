#!/bin/bash

# Script to set up the virtual environment and install dependencies

VENV_DIR="venv"

echo "[1/3] Creating virtual environment in $VENV_DIR..."
if [ -d "$VENV_DIR" ]; then
  echo "Virtual environment already exists. Skipping creation."
else
  python3 -m venv $VENV_DIR
fi

echo "[2/3] Activating environment and upgrading pip..."
source $VENV_DIR/bin/activate
pip install --upgrade pip

echo "[3/3] Installing project and dependencies from pyproject.toml..."
# Installing in editable mode (-e) so changes in src/ are reflected immediately
pip install -e .

echo "--------------------------------------------------"
echo "SETUP COMPLETE!"
echo "To start the simulation, run: ./run_sim.sh"
echo "--------------------------------------------------"

