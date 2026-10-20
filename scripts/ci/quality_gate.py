import sys
import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from fastapi.testclient import TestClient
from app.main import app

print("Running Quality Gate...")
# Get candidate again
with TestClient(app) as client:
    res = client.get("/api/v1/models/")
    models = res.json().get("models", [])
    candidates = [m for m in models if m["status"] == "CANDIDATE"]
    if not candidates:
        print("No CANDIDATE found to promote.")
        sys.exit(1)
    
    candidate = candidates[0]
    version = candidate["version"]
    
    promote_res = client.post(f"/api/v1/models/{version}/promote", headers={"X-API-Key": "secret-admin-key"})
    if promote_res.status_code == 200:
        decision = promote_res.json().get("decision")
        if decision == "PROMOTE":
            print("Quality gate passed! Model promoted to PRODUCTION.")
            sys.exit(0)
        else:
            print(f"Quality gate rejected candidate. Decision: {decision}. Reason: {promote_res.json().get('reason')}")
            sys.exit(1)
    else:
        print(f"Quality gate error: {promote_res.text}")
        sys.exit(1)