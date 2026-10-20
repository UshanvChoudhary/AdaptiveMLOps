import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    PROJECT_NAME: str = "AdaptiveMLOps"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str = "postgresql+psycopg2://postgres:fa8c513de6e0734a307047e47ffb862d@bdrb7j6b.ap-southeast.database.insforge.app:5432/insforge?ssl=require"
    BACKEND_CORS_ORIGINS: list[str] = []
    DEBUG: bool = False
    
    PRODUCTION_MODEL_DIR: str = os.path.join(BASE_DIR, "ml", "artifacts", "1.0.0")
    MIN_F1: float = 0.80
    MIN_ACCURACY: float = 0.80
    DRIFT_THRESHOLD_WARNING: float = 0.15
    DRIFT_THRESHOLD_CRITICAL: float = 0.30
    MIN_IMPROVEMENT: float = 0.01
    MAX_LATENCY_P95_MS: float = 100.0
    ADMIN_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, 'backend', '.env'), case_sensitive=True)

settings = Settings()
