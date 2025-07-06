import os
from pydantic_settings import BaseSettings
from core.services.parameterServiceAws import get_ssm_parameter

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Web Inference API"
    JWT_SECRET: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 semana
    DATABASE_URL: str
    SYSTEM_DATABASE_URL: str
    LOG_LEVEL: str = "info"
    BUCKET_NAME: str
    ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings(
        JWT_SECRET=get_ssm_parameter("/my-fastApi-app/JWT_SECRET"),
        DATABASE_URL=get_ssm_parameter("/my-fastApi-app/DATABASE_URL"),
        SYSTEM_DATABASE_URL=get_ssm_parameter("/my-fastApi-app/SYSTEM_DATABASE_URL"),
        BUCKET_NAME=get_ssm_parameter("/my-fastApi-app/BUCKET_NAME"),
        ENV="production"
    )
