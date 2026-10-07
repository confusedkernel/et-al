from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://etal:etal@localhost:5432/etal"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me"

    # "password": local accounts; "none": single-user mode, everyone is the local admin.
    auth_mode: Literal["password", "none"] = "password"
    allow_signup: bool = True
    session_ttl_days: int = 30
    cookie_secure: bool = False

    default_user_budget_usd: float = 10.0

    openrouter_api_key: str = ""
    sandbox_backend: Literal["docker", "e2b"] = "docker"
    search_backend: Literal["searxng", "exa", "tavily"] = "searxng"


@lru_cache
def get_settings() -> Settings:
    return Settings()
