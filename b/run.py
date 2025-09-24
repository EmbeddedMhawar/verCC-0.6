#!/usr/bin/env python3
"""
VerifiedCC Backend Startup Script
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting VerifiedCC Python Backend...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )