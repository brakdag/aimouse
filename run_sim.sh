#!/bin/bash

# Script to run the training simulation within the virtual environment

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Error: Virtual environment not found."
  echo "Please run ./setup_env.sh first."
  exit 1
fi

echo "Activating environment and launching simulation..."
source $VENV_DIR/bin/activate
python run_training.py

