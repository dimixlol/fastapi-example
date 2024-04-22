import logging
import uuid
from time import sleep
from typing import Any

from celery import shared_task

from src.application.core import context
from src.application.core.db import Message
from src.application.services.aws import S3Client
from src.application.services.database import get_sync_session

session = get_sync_session()
logger = logging.getLogger()


@shared_task()
def upload_to_s3(message_id: uuid.UUID, data: str) -> dict[str, str | Any]:
    logger.info(f"processing message {message_id}")
    message = Message.sync_get(session, id=message_id)
    if not message:
        logger.info("message not found")
        return {}
    s3 = S3Client(context.settings.aws)
    s3.upload(message.path, data)
    message.to_uploaded(session)
    logger.info(f"message {message_id} uploaded")
    sleep(2)
    return {
        "id": str(message.id),
        "link": message.link,
        "status": str(message.status),
        "message": data,
    }
