import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    BASE_DIR: str = BASE_DIR
    PROJECT_NAME: str = "AdaptiveMLOps"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/adaptive_mlops")
    )
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    DEBUG: bool = False
    ENABLE_DEMO_MODE: bool = os.getenv("ENABLE_DEMO_MODE", "false").lower() in ("true", "1", "yes")
    
    PRODUCTION_MODEL_DIR: str = os.path.join(BASE_DIR, "ml", "artifacts", "1.0.0")
    MIN_F1: float = 0.80
    MIN_ACCURACY: float = 0.80
    DRIFT_THRESHOLD_WARNING: float = 0.15
    DRIFT_THRESHOLD_CRITICAL: float = 0.30
    MIN_IMPROVEMENT: float = 0.01
    MAX_LATENCY_P95_MS: float = 100.0
    RETRAIN_FEEDBACK_THRESHOLD: int = 5
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "secret-admin-key")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-local-key-xyz123")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, 'backend', '.env'),
        case_sensitive=True,
        extra="allow"
    )

settings = Settings()
