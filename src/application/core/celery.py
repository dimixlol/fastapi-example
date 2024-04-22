from celery.app import Celery

from src.application.core.config import get_settings

celery_app = Celery(__name__)
celery_app.config_from_object(get_settings().celery)
celery_app.autodiscover_tasks()
