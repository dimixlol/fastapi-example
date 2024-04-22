import os
from pathlib import Path, PosixPath

from pydantic_settings import BaseSettings, SettingsConfigDict

from . import AWSSettings, CelerySettings, DBSettings, LoggingSettings


class Settings(BaseSettings):
    base_dir: PosixPath = Path(__file__).resolve().parent.parent.parent.parent
    aws: AWSSettings = AWSSettings()
    project_name: str = "sample"
    cookie_name: str = "auth_token"
    secret: str = "keep-your-eyes-to-yourself"
    db: DBSettings = DBSettings()
    celery: CelerySettings = CelerySettings()
    logging: LoggingSettings = LoggingSettings()
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'local')}",
        env_nested_delimiter="__",
        validate_default=False,
        extra="allow",
    )
