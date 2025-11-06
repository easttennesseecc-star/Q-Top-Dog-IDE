import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.main import app
from fastapi.testclient import TestClient

c = TestClient(app)
r = c.get('/health')
print(r.status_code)
print(r.text)
