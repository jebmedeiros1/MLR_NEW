from functools import lru_cache
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "mlr-backend"
    database_url: str = Field(..., env="DATABASE_URL")
    pi_base_url: Optional[AnyHttpUrl] = None
    pi_username: Optional[str] = None
    pi_password: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
