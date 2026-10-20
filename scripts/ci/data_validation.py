import sys
from fastapi.testclient import TestClient
import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
import sys

# Ensure backend module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
try:
    from app.main import app
    with TestClient(app) as client:
        # Simple hit to health endpoint to ensure DB connectivity
        res = client.get("/api/v1/health")
        if res.status_code != 200:
            print("Data validation / health check failed.")
            sys.exit(1)
        print("Data Validation passed.")
        sys.exit(0)
except Exception as e:
    print(f"Data Validation error: {e}")
    sys.exit(1)
