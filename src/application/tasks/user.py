import logging
import uuid

from celery import shared_task

from src.application.core import context
from src.application.core.db import User
from src.application.services.crypto import EncryptorServiceFactory
from src.application.services.database import get_sync_session
from src.application.services.sign_up import SignUpServiceFactory

session = get_sync_session()
logger = logging.getLogger()


@shared_task()
def sign_up_user(user_id: uuid.UUID, password: str) -> None:
    logger.info(f"signing up user {user_id}")
    user = User.sync_get(session, id=user_id)
    encryptor = EncryptorServiceFactory(context.settings).get()
    password = encryptor.decrypt(password)
    SignUpServiceFactory(context.settings.aws).get().sign_up(
        username=user.username, password=password, email=user.email
    )
    logger.info(f"user {user_id} signed up, confirmation email sent")
