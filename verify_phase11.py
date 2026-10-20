import subprocess
import time
import os
import sys
import requests

def run_cmd(cmd, cwd, env=None, shell=False):
    print(f"Running: {cmd} in {cwd}")
    result = subprocess.run(cmd, cwd=cwd, env=env, shell=shell)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}: {cmd}")
        return False
    return True

def wait_for_server(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200 or r.status_code == 404:  
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False

def main():
    workspace = r"C:\Users\USER\Desktop\Programs\adaptive-mlops"
    
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    env["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
    env["ADMIN_API_KEY"] = "admin_secret"
    env["FRONTEND_URL"] = "http://localhost:5173"

    print("=== Initialize DB ===")
    run_cmd(["python", "-m", "alembic", "upgrade", "head"], os.path.join(workspace, "backend"), env)

    print("=== 1 & 2. Backend Unit and Integration Tests ===")
    if not run_cmd(["python", "-m", "pytest", "backend/tests/"], workspace, env):
        sys.exit(1)

    print("=== 4. Frontend Build ===")
    if not run_cmd("npm run build", os.path.join(workspace, "frontend"), shell=True):
        sys.exit(1)

    print("=== 5. Selenium Tests ===")
    print("Starting backend...")
    backend = subprocess.Popen(
        "python -m uvicorn app.main:app --port 8000",
        cwd=os.path.join(workspace, "backend"),
        shell=True,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("Starting frontend (dev server)...")
    frontend = subprocess.Popen(
        "npm run dev -- --port 5173",
        cwd=os.path.join(workspace, "frontend"),
        shell=True,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("Waiting for servers to start...")
    wait_for_server("http://localhost:8000/docs")
    time.sleep(10) # give frontend time

    print("Running UI tests...")
    ui_result = run_cmd(["python", "-m", "pytest", "tests/e2e/test_ui.py", "-v"], workspace, env)

    print("Cleaning up servers...")
    os.system('taskkill /t /f /pid {}'.format(backend.pid))
    os.system('taskkill /t /f /pid {}'.format(frontend.pid))

    if not ui_result:
        sys.exit(1)

    print("=== All Verification Steps Passed! ===")

if __name__ == "__main__":
    main()
