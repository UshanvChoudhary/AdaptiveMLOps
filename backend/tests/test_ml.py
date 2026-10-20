import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
import pytest
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from app.ml.data_validation import load_and_clean_data
from app.ml.preprocessing import get_vectorizer
from app.ml.model import get_model
from app.ml.artifacts import save_artifact, load_artifact

async def test_data_validation(tmp_path):
    csv_file = tmp_path / "test.csv"
    df = pd.DataFrame({
        "text": ["A", "B", "A", None, "Invalid"],
        "intent": ["billing", "refund", "billing", "refund", "invalid_intent"]
    })
    df.to_csv(csv_file, index=False)
    
    cleaned = load_and_clean_data(str(csv_file))
    assert len(cleaned) == 2
    assert "A" in cleaned["text"].values
    assert "B" in cleaned["text"].values

async def test_preprocessing():
    vectorizer = get_vectorizer()
    X = vectorizer.fit_transform(["hello world", "world is great"])
    assert X.shape[0] == 2
    assert X.shape[1] > 0

async def test_deterministic_training():
    model1 = get_model(42)
    model2 = get_model(42)
    assert model1.random_state == model2.random_state

async def test_artifact_serialization(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    
    model = LogisticRegression()
    vectorizer = TfidfVectorizer()
    metadata = {"model_version": "test-1.0"}
    
    save_artifact(model, vectorizer, metadata, str(artifact_dir))
    
    loaded_model, loaded_vec, loaded_meta = load_artifact(str(artifact_dir))
    assert loaded_meta["model_version"] == "test-1.0"
    assert isinstance(loaded_model, LogisticRegression)
    assert isinstance(loaded_vec, TfidfVectorizer)
