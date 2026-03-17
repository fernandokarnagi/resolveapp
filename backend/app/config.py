from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongodb_url: str
    database_name: str = "resolveapp"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    gemini_api_key: Optional[str] = None
    ask_me_model: str = "gemini/gemini-2.0-flash-lite"

    class Config:
        env_file = ".env"


settings = Settings()
