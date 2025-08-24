#!/usr/bin/env python3
"""
WSGI entry point for Apache deployment
"""
import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set environment variables for production
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')

# Import the FastAPI app
from main import app

# WSGI application
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
