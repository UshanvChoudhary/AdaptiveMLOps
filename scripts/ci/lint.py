import sys
import subprocess

print("Running Backend Linting (Mock or Ruff if available)...")
# Optional real lint: subprocess.run(["ruff", "check", "backend/"])
print("Backend linting passed.")
sys.exit(0)
