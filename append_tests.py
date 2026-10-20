import sys

file_path = 'backend/tests/test_retraining.py'
with open(file_path, 'r') as f:
    content = f.read()

new_tests = '''
def test_retraining_no_eligible_feedback(client, db_session):
    # Trigger a manual job when there is no feedback
    response = client.post("/api/v1/retraining/trigger", json={
        "trigger_type": "MANUAL",
        "reason": "Test empty feedback"
    })
    assert response.status_code == 200
    job_id = response.json()["id"]

    # Wait for the background task to finish (since it uses sqlite, it might be fast, but we'll fetch explicitly)
    import time
    time.sleep(1) # wait for bg task

    response = client.get(f"/api/v1/retraining/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert "No eligible feedback" in data["error_message"]

def test_retraining_pagination(client, db_session):
    # Add some dummy jobs
    from app.db.models.retraining import RetrainingJob
    for i in range(5):
        db_session.add(RetrainingJob(
            trigger_type="MANUAL",
            feedback_count=0,
            status="COMPLETED"
        ))
    db_session.commit()

    response = client.get("/api/v1/retraining/jobs?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["jobs"]) == 2
'''

with open(file_path, 'a') as f:
    f.write(new_tests)
