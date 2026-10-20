import sys
import subprocess
import time
import os
import urllib.request
import json
import urllib.error

env = os.environ.copy()
env["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
env["RUN_E2E"] = "1"
env["PYTHONUNBUFFERED"] = "1"

db_path = r"C:\Users\USER\Desktop\Programs\adaptive-mlops\backend\test.db"
if os.path.exists(db_path):
    os.remove(db_path)

print("Running migrations...")
subprocess.run(
    ["python", "-m", "alembic", "upgrade", "head"],
    cwd=r"C:\Users\USER\Desktop\Programs\adaptive-mlops\backend",
    env=env,
    check=True
)

print("Starting backend...")
backend = subprocess.Popen(
    "python -m uvicorn app.main:app --port 8000",
    cwd=r"C:\Users\USER\Desktop\Programs\adaptive-mlops\backend",
    stdout=sys.stdout,
    stderr=sys.stderr,
    shell=True,
    env=env,
    text=True
)

time.sleep(5)

try:
    print("Making prediction...")
    req = urllib.request.Request("http://localhost:8000/api/v1/predictions/", data=json.dumps({"text": "help me reset password"}).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        res_text = res.read().decode()
        print(res.status, res_text)
        pred_id = json.loads(res_text)["prediction_id"]

    print("Submitting feedback...")
    req2 = urllib.request.Request(f"http://localhost:8000/api/v1/predictions/{pred_id}/feedback", data=json.dumps({
        "is_correct": False,
        "corrected_label": "technical_support",
        "comments": "User corrected"
    }).encode(), headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req2) as fb_res:
        print(fb_res.status, fb_res.read().decode())
except urllib.error.HTTPError as e:
    print(e)
    print(e.read().decode())
except Exception as e:
    print(e)

print("Cleaning up...")
os.system('taskkill /t /f /pid {}'.format(backend.pid))
