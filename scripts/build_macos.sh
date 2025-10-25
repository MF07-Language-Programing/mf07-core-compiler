#!/usr/bin/env bash
set -euo pipefail
if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script must be run on macOS"
  exit 1
fi
if [ -z "${VIRTUAL_ENV-}" ]; then
  echo "Please activate a virtualenv and install dependencies (pip install -r requirements.txt pyinstaller)"
  exit 1
fi
python -m pip install --upgrade pip
python -m pip install pyinstaller
pyinstaller --onefile --name mf mf.py
if [ -f dist/mf ]; then
  echo "Built dist/mf"
else
  echo "Build failed"
  exit 1
fi
