import sys
from datetime import datetime, timezone

file_path = 'backend/app/services/retraining_service.py'
with open(file_path, 'r') as f:
    content = f.read()

target = '''    job.status = "RUNNING"
    job.started_at = datetime.now(timezone.utc)
    db.commit()'''

replacement = '''    # Secondary concurrency check
    running_job = db.query(RetrainingJob).filter(RetrainingJob.status == "RUNNING").first()
    if running_job and running_job.id != job_id:
        job.status = "FAILED"
        job.error_message = "Aborted: Another job is currently running."
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        return

    job.status = "RUNNING"
    job.started_at = datetime.now(timezone.utc)
    db.commit()'''

content = content.replace(target, replacement)

with open(file_path, 'w') as f:
    f.write(content)
