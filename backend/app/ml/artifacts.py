import json
import joblib
import hashlib
import subprocess
import os
from datetime import datetime, timezone

def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
    except Exception:
        return "unknown"

def compute_checksum(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def save_artifact(model, vectorizer, metadata, artifact_dir):
    os.makedirs(artifact_dir, exist_ok=True)
    joblib.dump(model, os.path.join(artifact_dir, "model.joblib"))
    joblib.dump(vectorizer, os.path.join(artifact_dir, "vectorizer.joblib"))
    with open(os.path.join(artifact_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

def load_artifact(artifact_dir):
    model = joblib.load(os.path.join(artifact_dir, "model.joblib"))
    vectorizer = joblib.load(os.path.join(artifact_dir, "vectorizer.joblib"))
    with open(os.path.join(artifact_dir, "metadata.json"), "r") as f:
        metadata = json.load(f)
    return model, vectorizer, metadata
