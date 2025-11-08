#!/usr/bin/env python3
"""
Local development runner for Via India FastAPI application.
Run this from the via-india-lambda directory: python run_local.py
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Set up environment variables for local testing
os.environ.setdefault("USERS_TABLE_NAME", "via-india-users-local")
os.environ.setdefault("REQUESTS_TABLE_NAME", "via-india-requests-local")
os.environ.setdefault("MATCHES_TABLE_NAME", "via-india-matches-local")
os.environ.setdefault("AWS_REGION", "us-west-2")

if __name__ == "__main__":
    import uvicorn

    # Import the FastAPI app
    from main import app

    print("🚀 Starting Via India API locally...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled for development")
    print("\n" + "="*50)

    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
