import os
import sys
import argparse
import pandas as pd
from sklearn.metrics import classification_report

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from app.ml.artifacts import load_artifact

def evaluate(artifact_dir):
    model, vectorizer, metadata = load_artifact(artifact_dir)
    
    test_data_path = os.path.join(artifact_dir, "test_dataset.csv")
    if not os.path.exists(test_data_path):
        print(f"Error: test_dataset.csv not found in {artifact_dir}")
        return
        
    df = pd.read_csv(test_data_path)
    X_vec = vectorizer.transform(df['text'])
    y_pred = model.predict(X_vec)
    
    print("Classification Report on Unseen Test Data:")
    print(classification_report(df['intent'], y_pred, zero_division=0))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", required=True)
    args = parser.parse_args()
    evaluate(args.artifact_dir)
