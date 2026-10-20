import os
import urllib.parse
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load local environment configuration files if present
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "backend", ".env"))

def get_database_uri() -> str:
    # 1. Check explicit full URI environment variables
    explicit_uri = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
    if explicit_uri and explicit_uri.strip():
        return explicit_uri.strip()

    # 2. Check component environment variables
    host = os.getenv("POSTGRES_HOST") or os.getenv("DATABASE_HOST")
    password = os.getenv("POSTGRES_PASSWORD") or os.getenv("DATABASE_PASSWORD")

    if host and password:
        user = (
            os.getenv("POSTGRES_USER")
            or os.getenv("DATABASE_USER")
            or os.getenv("DATABASE_USERNAME")
            or "postgres"
        )
        port = os.getenv("POSTGRES_PORT") or os.getenv("DATABASE_PORT") or "5432"
        dbname = (
            os.getenv("POSTGRES_DB")
            or os.getenv("DATABASE_NAME")
            or os.getenv("DATABASE_DB")
            or "insforge"
        )
        sslmode = os.getenv("DATABASE_SSL_MODE") or os.getenv("POSTGRES_SSLMODE")
        if not sslmode:
            sslmode = "require" if ("insforge" in host or "supabase" in host or "amazonaws" in host) else ""

        encoded_password = urllib.parse.quote_plus(password)
        ssl_param = f"?sslmode={sslmode}" if sslmode else ""
        return f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{dbname}{ssl_param}"

    # 3. Default fallback to local Docker PostgreSQL service
    return "postgresql+psycopg2://postgres:postgres@localhost:5432/adaptive_mlops"

class Settings(BaseSettings):
    BASE_DIR: str = BASE_DIR
    PROJECT_NAME: str = "AdaptiveMLOps"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # InsForge API and Project Configuration
    INSFORGE_PROJECT_URL: str = os.getenv("INSFORGE_PROJECT_URL", "https://bdrb7j6b.ap-southeast.insforge.app")
    INSFORGE_API_KEY: str = os.getenv("INSFORGE_API_KEY", "")
    INSFORGE_ANON_KEY: str = os.getenv("INSFORGE_ANON_KEY", "")

    # Database Configuration
    SQLALCHEMY_DATABASE_URI: str = ""
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    DEBUG: bool = False
    ENABLE_DEMO_MODE: bool = os.getenv("ENABLE_DEMO_MODE", "true").lower() in ("true", "1", "yes")

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

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def validate_database_uri(cls, v):
        if not v or not str(v).strip():
            return get_database_uri()
        return str(v).strip()

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(BASE_DIR, ".env"),
            os.path.join(BASE_DIR, "backend", ".env"),
        ),
        case_sensitive=True,
        extra="allow",
    )

settings = Settings()
