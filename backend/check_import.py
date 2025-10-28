#!/usr/bin/env python3
import sys
import os

# Add backend directory to path
backend_dir = r"C:\Quellum-topdog-ide\backend"
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

try:
    print("\nTrying to import main...")
    import main
    print("OK - Successfully imported main")
    print(f"OK - FastAPI app: {main.app}")
    print(f"OK - Number of routes: {len(main.app.routes)}")
    
    # Check if llm_config routes are there
    llm_routes = [r for r in main.app.routes if hasattr(r, 'path') and '/llm_config' in r.path]
    print(f"OK - Number of LLM config routes: {len(llm_routes)}")
    for r in llm_routes:
        print(f"  - {r.path}")
except Exception as e:
    print(f"ERROR - Import failed: {e}")
    import traceback
    traceback.print_exc()

