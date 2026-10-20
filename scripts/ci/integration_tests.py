import sys
import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from fastapi.testclient import TestClient
from app.main import app

print("Running API Integration Tests...")
with TestClient(app) as client:
    res = client.post("/api/v1/predictions/", json={"text": "Integration test sample"})
    if res.status_code == 200:
        print("Integration test passed: API returned prediction.")
        sys.exit(0)
    else:
        print(f"Integration test failed: {res.status_code} {res.text}")
        sys.exit(1)
