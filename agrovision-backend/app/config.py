import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://agro_user:agro_secure_pass@localhost:5432/agrovision_main")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    INFERENCE_SERVICE_URL: str = os.getenv("INFERENCE_SERVICE_URL", "http://localhost:8080/predictions/crop_disease")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_jwt_signature_key_change_in_production")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "test_key")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "test_secret")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "agrovision-scans")

    class Config:
        env_file = ".env"

settings = Settings()
