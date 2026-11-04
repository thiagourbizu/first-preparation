import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cambridge B2 First Practice Platform"
    ENVIRONMENT: str = "production"
    ADMIN_PASSWORD: str = "admin123"
    SECRET_KEY: str = "change-this-secret-key-in-production-12345"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'fce.db'}"
    DATA_RAW_DIR: str = str(BASE_DIR.parent.parent / "old_proyect" / "first-practice" / "data")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
