#!/usr/bin/env python
"""
Quick start script for backend server
Starts uvicorn directly with proper module path
"""

import sys
import os
import subprocess

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Start uvicorn
try:
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ], cwd=os.path.join(os.path.dirname(__file__), 'backend'))
except KeyboardInterrupt:
    print("\n✓ Server stopped")
