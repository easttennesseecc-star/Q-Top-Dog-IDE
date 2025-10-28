#!/usr/bin/env python3
"""
Minimal backend server starter
Just runs uvicorn without fancy logging
"""
import sys
import os

# Change to backend directory
os.chdir(r"C:\Quellum-topdog-ide\backend")
sys.path.insert(0, r"C:\Quellum-topdog-ide\backend")

# Set environment to production
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
