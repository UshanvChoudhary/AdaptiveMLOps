import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from app.main import app as fastapi_app


API_KEY = os.getenv("API_KEY", "secret-admin-key")
BUILD_NUMBER = os.getenv("BUILD_NUMBER", "1")
GIT_SHA = os.getenv("GIT_SHA", "abcdef")

def deploy():
    with TestClient(fastapi_app) as client:
        print(f"Deploying image {BUILD_NUMBER}-{GIT_SHA}...")
        
        res = client.get("/api/v1/models")
        if res.status_code != 200:
            print(f"Failed to fetch models: {res.text}")
            sys.exit(1)
        
        models = res.json()["models"]
        approved_models = [m for m in models if m["status"] == "PRODUCTION"]
        if not approved_models:
            print("No PRODUCTION models to deploy.")
            sys.exit(1)
        
        model_to_deploy = approved_models[0]
    
        dep_req = {
            "model_version_id": model_to_deploy["id"],
            "image_tag": f"{BUILD_NUMBER}-{GIT_SHA}",
            "environment": "STAGING",
            "actor": "jenkins"
        }
    
        res = client.post("/api/v1/deployments", json=dep_req, headers={"X-API-Key": API_KEY})
        if res.status_code != 200:
            print(f"Failed to create deployment: {res.text}")
            sys.exit(1)
        
        dep_data = res.json()
        print(f"Deployment registered: {dep_data['id']}")
    
        with open(".deployment_id", "w") as f:
            f.write(dep_data["id"])

if __name__ == "__main__":
    deploy()
