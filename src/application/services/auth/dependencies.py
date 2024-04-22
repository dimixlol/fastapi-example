from typing import Annotated

from fastapi import Security
from jose import jwt
from starlette.requests import Request

from src.application.core.config import get_settings
from src.application.core.db import User
from src.application.core.exceptions import UnauthorizedException
from src.application.dependencies import AsyncDBSessionDepends
from src.application.services.aws import CognitoClient

from .extractors import CookieExtractor
from .jwt import JWTValidator

settings = get_settings()


async def get_current_user(
    session: AsyncDBSessionDepends, request: Request = None, token: str | None = None
):
    token = token or CookieExtractor(settings)(request)
    validator = JWTValidator(CognitoClient(settings.aws))
    if validator.is_valid(token):
        username = jwt.get_unverified_claims(token)["username"]
        if user := await User.async_get(session, username=username):
            return user
    raise UnauthorizedException("invalid token")


async def get_valid_token(request: Request):
    return JWTValidator.from_request(CognitoClient(settings.aws))(request)


CurrentUserDep = Annotated[User, Security(get_current_user)]
ValidTokenDep = Annotated[str, Security(get_valid_token)]
