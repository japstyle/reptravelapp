#!/usr/bin/env python3
"""
Startup script for Replit environment.
Runs FastAPI app on 0.0.0.0:5000
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
