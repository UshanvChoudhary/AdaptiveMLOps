import subprocess
import time
import os
import urllib.request
import json

env = os.environ.copy()
env["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
env["RUN_E2E"] = "1"

db_path = r"C:\Users\USER\Desktop\Programs\adaptive-mlops\backend\test.db"
if os.path.exists(db_path):
    os.remove(db_path)

subprocess.run(
    ["python", "-m", "alembic", "upgrade", "head"],
    cwd=r"C:\Users\USER\Desktop\Programs\adaptive-mlops\backend",
    env=env,
    check=True,
    stdout=subprocess.DEVNULL
)

print("Starting backend...")
backend = subprocess.Popen(
    "python -m uvicorn app.main:app --port 8000",
    cwd=r"C:\Users\USER\Desktop\Programs\adaptive-mlops\backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
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
except Exception as e:
    print(e)
    if hasattr(e, 'read'):
        print(e.read().decode())

print("Cleaning up...")
backend.terminate()
os.system('taskkill /f /im uvicorn.exe >nul 2>&1')

stdout, stderr = backend.communicate(timeout=2)
print("Backend Stdout:")
print(stdout)
print("Backend Stderr:")
print(stderr)
