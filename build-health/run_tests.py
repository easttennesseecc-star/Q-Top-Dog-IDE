"""
Test Runner Script for Q-IDE
Runs backend and frontend tests for integration and unit test coverage.
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

# Run backend tests
run_command('C:/Quellum-topdog-ide/.venv/Scripts/python.exe -m unittest discover backend')

# Run frontend tests (if available)
run_command('cd frontend && pnpm test')
