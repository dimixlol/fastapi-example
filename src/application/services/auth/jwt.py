import logging
import time
from typing import Callable

from jose import jwk, jwt
from jose.utils import base64url_decode
from starlette.requests import Request

from src.application.core.config import get_settings
from src.application.core.exceptions import UnauthorizedException
from src.application.services.aws.cognito import CognitoClient
from src.application.services.aws.exceptions import AWSException

from .exceptions import JWTHeaderVerificationFailed, JWTTokenVerificationFailed
from .extractors import CookieExtractor

logger = logging.getLogger()


class JWTValidator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(JWTValidator, cls).__new__(cls)
        return cls._instance

    def __init__(self, client: CognitoClient):
        self.cognito = client

    def get_valid_token(self, token):
        try:
            self._validate_token(token)
        except Exception as err:
            logger.warning(err)
        return token

    def is_valid(
        self, token: str, raise_exception=True, exception_cls=UnauthorizedException
    ) -> bool:
        try:
            self._validate_token(token)
        except Exception as err:
            if raise_exception:
                raise exception_cls("invalid token") from err
            return False
        return True

    def _validate_token(self, token):
        self._is_valid_jwt(token)
        self._verify_header(token)
        self._get_verified_claims(token)

    def _is_valid_jwt(self, token):
        try:
            jwt.get_unverified_header(token)
            jwt.get_unverified_claims(token)
        except jwt.JWTError as err:
            logger.debug(f"Failed to decode JWT token: {err}")
            raise
        return True

    def _verify_header(self, token):
        headers = jwt.get_unverified_header(token)
        kid = headers["kid"]

        cognito_jwk = self.cognito.get_pool_jwks()
        if not cognito_jwk:
            logger.error("Unable to retrieve JWKS from Cognito")
            raise AWSException("Failed to retrieve JWKS from Cognito")

        if cognito_jwk.kid != kid:
            logger.debug(f"Unable to find a signing key that matches '{kid}'")
            raise JWTHeaderVerificationFailed(
                f"Unable to find a signing key for '{kid}'"
            )

        key = jwk.construct(cognito_jwk.dict())
        if not key:
            logger.debug("Unable to construct key from JWKS")
            raise JWTHeaderVerificationFailed("Unable to construct key from JWKS")

        message, encoded_signature = str(token).rsplit(".", 1)
        signature = base64url_decode(encoded_signature.encode("utf-8"))

        if not key.verify(message.encode("utf8"), signature):
            logger.debug("Signature verification failed")
            raise JWTHeaderVerificationFailed("Invalid JWT not verify")

        return headers

    def _get_verified_claims(self, token: str) -> dict:
        claims = jwt.get_unverified_claims(token)

        if claims["exp"] < time.time():
            logger.debug("Token expired")
            raise JWTTokenVerificationFailed("Token is expired")

        if claims["iss"] != self.cognito.get_pool_issuer_url():
            logger.debug("Invalid issuer claim")
            raise JWTTokenVerificationFailed("Ivalid  issuer")

        if claims["client_id"] != self.cognito.get_client_id():
            logger.debug("Invalid audience claim")
            raise JWTTokenVerificationFailed("Invalid audience")

        if claims["token_use"] != "access":
            logger.debug("Invalid token use claim")
            raise JWTTokenVerificationFailed("Invalid token use")

        return claims

    @classmethod
    def from_request(
        cls,
        client: CognitoClient,
        token_extractor: Callable[[Request], str] = CookieExtractor(get_settings()),
    ):
        validator = cls(client)
        return lambda req: validator.get_valid_token(token_extractor(req))
