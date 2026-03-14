# shortener_app/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env_name: str
    base_url: str
    db_url: str
    secret_key: str
    algorithm: str = "HS256"
    token_expire_hours: int = 2
    
    model_config = {"env_file": ".env", "case_sensitive": False}

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings
