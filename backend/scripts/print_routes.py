import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.main import app

paths = sorted({getattr(r, 'path', None) for r in app.routes})
for p in paths:
    if p:
        print(p)
