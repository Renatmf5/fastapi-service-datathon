from pydantic_settings import BaseSettings
from core.services.parameterServiceAws import get_ssm_parameter
import os

class Settings(BaseSettings):
    # Configurations
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Web Inference API"
    # Security
    JWT_SECRET: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 60 minutos * 24 horas * 7 dias => 1 semana
    # Database
    DATABASE_URL: str
    # System Database
    SYSTEM_DATABASE_URL: str
    # Logging
    LOG_LEVEL: str = "info"
    # DataLake Bucket name
    BUCKET_NAME: str
    # Environment
    ENV: str = "development"

    class Config:
        env_file = ".env"

if os.getenv('ENV') == 'production':
    settings = Settings(
        JWT_SECRET=get_ssm_parameter("/my-fastApi-app/JWT_SECRET"),
        DATABASE_URL=get_ssm_parameter("/my-fastApi-app/DATABASE_URL"),
        SYSTEM_DATABASE_URL=get_ssm_parameter("/my-fastApi-app/SYSTEM_DATABASE_URL"),
        BUCKET_NAME=get_ssm_parameter("/my-fastApi-app/BUCKET_NAME")
    )
else:
    settings = Settings()