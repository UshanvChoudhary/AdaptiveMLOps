import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from fastapi.testclient import TestClient
from app.main import app
print("Running API Integration Tests...")
res = client.post("/api/v1/predictions/", json={"text": "Integration test sample"})
if res.status_code == 200:
    print("Integration test passed: API returned prediction.")
    sys.exit(0)
else:
    print("Integration test failed.")
    sys.exit(1)
