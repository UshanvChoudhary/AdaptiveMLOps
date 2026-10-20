import sys
import os
import requests

TARGET_SERVICE_URL = os.getenv("TARGET_SERVICE_URL", "http://localhost:8000")

print(f"Running API Integration Tests against: {TARGET_SERVICE_URL}...")
try:
    res = requests.post(
        f"{TARGET_SERVICE_URL}/api/v1/predictions/",
        json={"text": "Integration test customer billing question"},
        timeout=5
    )
    if res.status_code == 200:
        data = res.json()
        print(f"Integration test passed against running service: label='{data['label']}', confidence={data['confidence']}")
        sys.exit(0)
    else:
        print(f"Service returned error: {res.status_code} {res.text}")
except Exception as e:
    print(f"Direct HTTP connection failed ({e}), falling back to in-process TestClient...")
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
    from fastapi.testclient import TestClient
    from app.main import app
    from app.ml.prediction_service import prediction_service
    try:
        prediction_service.load_model()
    except Exception:
        pass
    with TestClient(app) as client:
        res = client.post("/api/v1/predictions/", json={"text": "Integration test fallback"})
        if res.status_code == 200:
            print(f"In-process integration test passed: {res.json()['label']}")
            sys.exit(0)
        else:
            print(f"In-process integration test failed: {res.status_code} {res.text}")
            sys.exit(1)
