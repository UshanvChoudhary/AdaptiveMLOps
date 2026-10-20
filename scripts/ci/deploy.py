import os
import sys
import requests
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from app.main import app as fastapi_app

API_KEY = os.getenv("ADMIN_API_KEY", os.getenv("API_KEY", "secret-admin-key"))
BUILD_NUMBER = os.getenv("BUILD_NUMBER", "1")
GIT_SHA = os.getenv("GIT_SHA", "abcdef")
TARGET_SERVICE_URL = os.getenv("TARGET_SERVICE_URL")

def deploy():
    print(f"Deploying candidate image {BUILD_NUMBER}-{GIT_SHA}...")
    headers = {"X-API-Key": API_KEY}
    
    if TARGET_SERVICE_URL:
        print(f"Targeting real deployed service at: {TARGET_SERVICE_URL}")
        res = requests.get(f"{TARGET_SERVICE_URL}/api/v1/models/", headers=headers)
        if res.status_code != 200:
            print(f"Failed to fetch models: {res.text}")
            sys.exit(1)
        models = res.json()["models"]
        approved = [m for m in models if m["status"] in ("PRODUCTION", "APPROVED")]
        if not approved:
            print("No PRODUCTION or APPROVED models to deploy.")
            sys.exit(1)
        model_to_deploy = approved[0]
        dep_req = {
            "model_version_id": model_to_deploy["id"],
            "image_tag": f"{BUILD_NUMBER}-{GIT_SHA}",
            "environment": "STAGING",
            "actor": "jenkins"
        }
        res = requests.post(f"{TARGET_SERVICE_URL}/api/v1/deployments", json=dep_req, headers=headers)
        if res.status_code != 200:
            print(f"Failed to create deployment: {res.text}")
            sys.exit(1)
        dep_data = res.json()
    else:
        print("Targeting in-process test client for deployment verification...")
        with TestClient(fastapi_app) as client:
            res = client.get("/api/v1/models/", headers=headers)
            if res.status_code != 200:
                print(f"Failed to fetch models: {res.text}")
                sys.exit(1)
            models = res.json()["models"]
            approved = [m for m in models if m["status"] in ("PRODUCTION", "APPROVED")]
            if not approved:
                print("No PRODUCTION or APPROVED models to deploy.")
                sys.exit(1)
            model_to_deploy = approved[0]
            dep_req = {
                "model_version_id": model_to_deploy["id"],
                "image_tag": f"{BUILD_NUMBER}-{GIT_SHA}",
                "environment": "STAGING",
                "actor": "jenkins"
            }
            res = client.post("/api/v1/deployments", json=dep_req, headers=headers)
            if res.status_code != 200:
                print(f"Failed to create deployment: {res.text}")
                sys.exit(1)
            dep_data = res.json()
            
    print(f"Deployment successfully registered: {dep_data['id']}")
    with open(".deployment_id", "w") as f:
        f.write(dep_data["id"])

if __name__ == "__main__":
    deploy()
