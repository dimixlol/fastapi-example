import os
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    url: str = "postgresql+asyncpg://sample:sample@localhost:5432/sample"
    url_sync: str = "postgresql://sample:sample@localhost:5432/sample"
    connection_kwargs: dict[str, Any] = {}
    session_kwargs: dict[str, Any] = {"autocommit": False, "expire_on_commit": False}
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'local')}",
        env_prefix="DB_",
        validate_default=False,
        extra="allow",
    )
