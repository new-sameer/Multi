#!/usr/bin/env python3
"""
Server entry point - imports from main.py
"""

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)