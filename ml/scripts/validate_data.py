import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from app.ml.data_validation import load_and_clean_data

def validate(data_path):
    df = load_and_clean_data(data_path)
    print(f"Dataset valid. {len(df)} rows after cleaning.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()
    validate(args.data)
