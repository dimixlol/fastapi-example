from enum import StrEnum

from sqlalchemy import Text, TypeDecorator

from src.application.core import context
from src.application.services.crypto import EncryptorService, EncryptorServiceFactory


class Status(StrEnum):
    pending = "pending"
    uploaded = "uploaded"


class Password(TypeDecorator):  # pylint: disable=(abstract-method
    impl = Text
    _crypto_factory = EncryptorServiceFactory(context.settings)

    @classmethod
    def get_crypto(cls) -> EncryptorService:
        return cls._crypto_factory.get()

    def process_bind_param(self, value, dialect):
        return self.get_crypto().encrypt(value)

    def process_result_value(self, value, dialect):
        return self.get_crypto().decrypt(value)
