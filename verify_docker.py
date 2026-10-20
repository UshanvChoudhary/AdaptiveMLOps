import subprocess
import os

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, cwd=cwd, check=True)

try:
    workspace = r"C:\Users\USER\Desktop\Programs\adaptive-mlops"
    run_cmd("docker-compose build", cwd=workspace)
    print("Docker build successful!")
except Exception as e:
    print(e)
