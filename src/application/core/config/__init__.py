from functools import lru_cache

from .aws import AWSSettings
from .celery import CelerySettings
from .db import DBSettings
from .logging import LoggingSettings
from .settings import Settings


@lru_cache
def get_settings():
    return Settings()


__all__ = (
    "get_settings",
    "Settings",
    "AWSSettings",
    "DBSettings",
    "CelerySettings",
    "LoggingSettings",
)
