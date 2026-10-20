import os
import sys
import time
import requests
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from app.main import app as fastapi_app
from app.ml.prediction_service import prediction_service

API_KEY = os.getenv("ADMIN_API_KEY", os.getenv("API_KEY", "secret-admin-key"))
TARGET_SERVICE_URL = os.getenv("TARGET_SERVICE_URL")

def check_endpoint_live(name, path, method="GET", json=None):
    start = time.time()
    try:
        url = f"{TARGET_SERVICE_URL}{path}"
        if method == "GET":
            res = requests.get(url, timeout=5)
        else:
            res = requests.post(url, json=json, timeout=5)
        duration = int((time.time() - start) * 1000)
        return {
            "endpoint": name,
            "status_code": str(res.status_code),
            "response_time_ms": str(duration),
            "is_healthy": res.status_code == 200,
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

def check_endpoint_testclient(name, path, method="GET", json=None):
    with TestClient(fastapi_app) as client:
        start = time.time()
        try:
            if method == "GET":
                res = client.get(path)
            else:
                res = client.post(path, json=json)
            duration = int((time.time() - start) * 1000)
            return {
                "endpoint": name,
                "status_code": str(res.status_code),
                "response_time_ms": str(duration),
                "is_healthy": res.status_code == 200,
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
    headers = {"X-API-Key": API_KEY}
    
    if TARGET_SERVICE_URL:
        print(f"Performing health checks against running service at: {TARGET_SERVICE_URL}")
        checks = [
            check_endpoint_live("/health", "/api/v1/health"),
            check_endpoint_live("/ready", "/api/v1/ready"),
            check_endpoint_live("predictions", "/api/v1/predictions/", method="POST", json={"text": "Service health check probe"})
        ]
        all_healthy = all(c["is_healthy"] for c in checks)
        for c in checks:
            print(f"{c['endpoint']}: healthy={c['is_healthy']} (HTTP {c['status_code']} in {c['response_time_ms']}ms)")
            requests.post(f"{TARGET_SERVICE_URL}/api/v1/deployments/{dep_id}/health", json=c, headers=headers)
        
        status = "SUCCESS" if all_healthy else "FAILED"
        print(f"Deployment status resolved: {status}")
        requests.patch(f"{TARGET_SERVICE_URL}/api/v1/deployments/{dep_id}", json={"status": status}, headers=headers)
    else:
        print("Performing health checks using TestClient harness...")
        try:
            prediction_service.load_model()
        except Exception:
            pass
        checks = [
            check_endpoint_testclient("/health", "/api/v1/health"),
            check_endpoint_testclient("/ready", "/api/v1/ready"),
            check_endpoint_testclient("predictions", "/api/v1/predictions/", method="POST", json={"text": "TestClient health probe"})
        ]
        all_healthy = all(c["is_healthy"] for c in checks)
        with TestClient(fastapi_app) as client:
            for c in checks:
                print(f"{c['endpoint']}: healthy={c['is_healthy']} (HTTP {c['status_code']} in {c['response_time_ms']}ms)")
                client.post(f"/api/v1/deployments/{dep_id}/health", json=c, headers=headers)
            
            status = "SUCCESS" if all_healthy else "FAILED"
            print(f"Deployment status resolved: {status}")
            client.patch(f"/api/v1/deployments/{dep_id}", json={"status": status}, headers=headers)
            
    if not all_healthy:
        print("Health checks failed. Deployment aborted and marked FAILED.")
        sys.exit(1)
        
    print("All health checks passed. Deployment marked SUCCESS.")

if __name__ == "__main__":
    run_health_checks()
