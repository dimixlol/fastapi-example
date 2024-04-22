from logging.config import dictConfig

from src.application.core.config import get_settings


def configure_logging():
    dictConfig(get_settings().logging.dict())
