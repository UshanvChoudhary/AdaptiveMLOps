import os
import sys
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.ml.data_validation import load_and_clean_data
from app.ml.preprocessing import get_vectorizer
from app.ml.model import get_model
from app.ml.artifacts import compute_checksum, get_git_commit, save_artifact

def train(data_path, artifact_dir, seed=42):
    df = load_and_clean_data(data_path)
    checksum = compute_checksum(data_path)
    
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['intent'], test_size=0.2, random_state=seed, stratify=df['intent']
    )
    
    os.makedirs(artifact_dir, exist_ok=True)
    test_df = pd.DataFrame({'text': X_test, 'intent': y_test})
    test_df.to_csv(os.path.join(artifact_dir, "test_dataset.csv"), index=False)
    
    vectorizer = get_vectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    
    model = get_model(random_seed=seed)
    model.fit(X_train_vec, y_train)
    
    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
        "f1_score": f1_score(y_test, y_pred, average='weighted', zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }
    
    metadata = {
        "model_version": "1.0.0",
        "algorithm": "Logistic Regression + TF-IDF",
        "dataset_version": "demo",
        "dataset_checksum": checksum,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "hyperparameters": model.get_params(),
        "evaluation_metrics": metrics,
        "source_git_commit": get_git_commit()
    }
    
    save_artifact(model, vectorizer, metadata, artifact_dir)
    print("Training complete. Metrics:", metrics)
    print(f"Test dataset saved to {os.path.join(artifact_dir, 'test_dataset.csv')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    train(args.data, args.artifact_dir, args.seed)
