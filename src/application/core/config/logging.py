import os
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    version: int = 1
    disable_existing_loggers: bool = True
    formatters: dict[str, dict[str, Any]] = {
        "default": {
            "format": "%(asctime)s: %(name)s: %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    }
    handlers: dict[str, dict[str, Any]] = {
        "console": {"class": "logging.StreamHandler", "formatter": "default"}
    }
    loggers: dict[str, dict[str, Any]] = {
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'local')}",
        env_prefix="LOGGING_",
        validate_default=False,
        extra="allow",
    )
