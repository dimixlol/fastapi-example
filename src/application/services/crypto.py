from base64 import urlsafe_b64encode
from functools import lru_cache
from typing import Protocol

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.application.core.config import Settings


class EncryptorService(Protocol):
    def encrypt(self, data: str) -> str:
        pass

    def decrypt(self, data: str) -> str:
        pass


class SymmetricEncryptor:
    key_length: int = 32
    key_algorithm: hashes.HashAlgorithm = hashes.SHA512()
    key_iterations: int = 720000

    def __init__(self, secret: bytes | str, salt: bytes | str = None) -> None:
        if salt is None:
            salt = self.__class__.__name__
        key = self._derive(self.force_bytes(secret), self.force_bytes(salt))
        self.cipher = Fernet(key)

    @lru_cache
    def _derive(self, key: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=self.key_algorithm,
            length=self.key_length,
            salt=salt,
            iterations=self.key_iterations,
        )
        return urlsafe_b64encode(kdf.derive(key))

    @staticmethod
    def force_bytes(key: bytes | str) -> bytes:
        if isinstance(key, str):
            key = key.encode("utf-8")
        return key

    def encrypt(self, data: bytes | str) -> str:
        return self.cipher.encrypt(self.force_bytes(data)).decode("utf-8")

    def decrypt(self, data: bytes | str) -> str:
        return self.cipher.decrypt(self.force_bytes(data)).decode("utf-8")


class EncryptorServiceFactory:
    _encryptor = None

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get(self) -> EncryptorService:
        if self._encryptor is None:
            self._encryptor = SymmetricEncryptor(self.settings.secret)
        return self._encryptor
