import os
from typing import Tuple
from app.ml.artifacts import load_artifact
from app.config import settings

class PredictionService:
    def __init__(self, artifact_dir: str):
        self.artifact_dir = artifact_dir
        self.model = None
        self.vectorizer = None
        self.metadata = None
        
    def load_model(self):
        try:
            if not os.path.exists(self.artifact_dir):
                print(f"Warning: Model artifacts not found at {self.artifact_dir}")
                return
            self.model, self.vectorizer, self.metadata = load_artifact(self.artifact_dir)
        except Exception as e:
            print(f"Warning: Failed to load production model: {e}")
        
    def predict(self, text: str) -> Tuple[str, float, str]:
        if not self.model or not self.vectorizer:
            self.load_model()
        if not self.model or not self.vectorizer:
            raise RuntimeError("Model is not loaded.")
            
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        
        probabilities = self.model.predict_proba(X)[0]
        confidence = max(probabilities)
        
        version = self.metadata.get("model_version", "unknown")
        
        return prediction, confidence, version

prediction_service = PredictionService(settings.PRODUCTION_MODEL_DIR)
