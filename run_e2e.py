import subprocess
import time
import os
import sys

env = os.environ.copy()
env["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
env["RUN_E2E"] = "1"
env["PYTHONUNBUFFERED"] = "1"

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
    shell=True,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print("Starting frontend...")
frontend = subprocess.Popen(
    "npm run dev",
    cwd=r"C:\Users\USER\Desktop\Programs\adaptive-mlops\frontend",
    shell=True,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(10)

print("Running E2E tests...")
env["PYTHONPATH"] = "backend"
res = subprocess.run(
    ["python", "-m", "pytest", "tests/e2e/test_feedback_flow.py", "-v"],
    cwd=r"C:\Users\USER\Desktop\Programs\adaptive-mlops",
    env=env
)

print("Cleaning up...")
os.system('taskkill /t /f /pid {}'.format(backend.pid))
os.system('taskkill /t /f /pid {}'.format(frontend.pid))

sys.exit(res.returncode)
