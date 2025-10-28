#!/usr/bin/env python3
"""
Backend server launcher
Runs the FastAPI backend with proper error handling
"""

import sys
import os
import subprocess

# Add backend to Python path
backend_dir = r"C:\Quellum-topdog-ide\backend"
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

print(f"[*] Working directory: {os.getcwd()}")
print(f"[*] Python: {sys.executable}")
print(f"[*] Starting FastAPI backend on 127.0.0.1:8000...")
print()

# Try to run the server
try:
    from uvicorn import run
    run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True
    )
except KeyboardInterrupt:
    print("\n[!] Server stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"[!] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
