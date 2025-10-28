# Ensure parent directory is on sys.path so `backend` package imports resolve
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
