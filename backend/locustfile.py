from locust import HttpUser, task, between

class MLOpsUser(HttpUser):
    wait_time = between(0.1, 1.0)
    
    @task
    def predict(self):
        self.client.post("/api/v1/predict", json={
            "features": {"text": "This is a test request for load testing."}
        })
