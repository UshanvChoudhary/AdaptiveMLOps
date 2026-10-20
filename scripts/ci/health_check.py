import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
import sys
import time
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from app.main import app as fastapi_app

from app.ml.prediction_service import prediction_service
prediction_service.load_model()

API_KEY = os.getenv("API_KEY", "secret-admin-key")

def check_endpoint(name, url, method="GET", json=None):
    with TestClient(fastapi_app) as client:
        start = time.time()
        try:
            if method == "GET":
                res = client.get(url)
            else:
                res = client.post(url, json=json)
            duration = int((time.time() - start) * 1000)
            is_healthy = res.status_code == 200
            return {
                "endpoint": name,
                "status_code": str(res.status_code),
                "response_time_ms": str(duration),
                "is_healthy": is_healthy,
                "details": res.text[:200]
            }
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return {
                "endpoint": name,
                "status_code": "ERROR",
                "response_time_ms": str(duration),
                "is_healthy": False,
                "details": str(e)
            }

def run_health_checks():
    if not os.path.exists(".deployment_id"):
        print("No .deployment_id found. Skipping health checks.")
        sys.exit(1)
    
    with open(".deployment_id", "r") as f:
        dep_id = f.read().strip()
    
    print(f"Running health checks for deployment {dep_id}...")
    
    checks = [
        check_endpoint("/health", "/api/v1/health"),
        check_endpoint("/ready", "/api/v1/ready"),
        check_endpoint("predictions", "/api/v1/predictions", method="POST", json={"text": "test data"})
    ]
    
    all_healthy = all(c["is_healthy"] for c in checks)
    
    with TestClient(fastapi_app) as client:
        for c in checks:
            print(f"{c['endpoint']}: {c['is_healthy']} ({c['status_code']} in {c['response_time_ms']}ms)")
            res = client.post(f"/api/v1/deployments/{dep_id}/health", json=c, headers={"X-API-Key": API_KEY})
        
        status = "SUCCESS" if all_healthy else "FAILED"
        print(f"Deployment status: {status}")
    
        client.patch(f"/api/v1/deployments/{dep_id}", json={"status": status}, headers={"X-API-Key": API_KEY})
    
    if not all_healthy:
        print("Health checks failed. Deployment aborted.")
        sys.exit(1)
    
    print("Health checks passed. Deployment successful.")

if __name__ == "__main__":
    run_health_checks()
