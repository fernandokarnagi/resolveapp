#!/bin/bash
cd "$(dirname "$0")/backend"
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  /opt/homebrew/bin/python3.12 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -q
echo "Starting FastAPI backend on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
