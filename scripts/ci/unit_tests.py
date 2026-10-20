import subprocess
import sys
import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'

def main():
    print("Running backend unit tests...")
    env = os.environ.copy()
    # Ensure test.db is used for unit tests locally, but DB URL can be overridden
    result = subprocess.run(["python", "-m", "pytest", "tests/", "--junitxml=junit-report.xml"], cwd="backend", env=env)
    if result.returncode != 0:
        print("Unit tests failed!")
        sys.exit(result.returncode)
    print("Unit tests passed.")

if __name__ == "__main__":
    main()
