"""
Build Health Check Script for Q-IDE
Checks backend and frontend build/test status for robustness and stability.
"""
import subprocess
import sys

def run_command(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)

# Check Python backend tests
run_command('C:/Quellum-topdog-ide/.venv/Scripts/python.exe -m unittest discover backend')

# Check frontend build
run_command('cd frontend && pnpm run build')
