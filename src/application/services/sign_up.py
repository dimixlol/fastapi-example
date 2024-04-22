import logging
from typing import Protocol

from src.application.core.exceptions import BusinessException, UnhandledException
from src.application.services.aws import CognitoClient

logger = logging.getLogger()


class ConfirmationFailedException(BusinessException):
    pass


class SignUpFailedException(BusinessException):
    pass


class SignUpService(Protocol):
    def sign_up(self, username: str, password: str, email: str):
        pass

    def confirm(self, username: str, code: str):
        pass


class CognitoSignUpService:
    def __init__(self, cognito: CognitoClient):
        self.cognito = cognito

    @classmethod
    def from_settings(cls, settings):
        return cls(CognitoClient(settings))

    def confirm(self, username: str, code: str):
        cid = self.cognito.get_client_id()
        error_msg = "failed to confirm registration"
        try:
            self.cognito.client.confirm_sign_up(
                ClientId=cid,
                Username=username,
                ConfirmationCode=code,
            )
        except self.cognito.client.exceptions.UserNotFoundException as err:
            logger.warning(f"{error_msg}: user with username {username} doesnt exists")
            raise ConfirmationFailedException("username doesnt exists") from err
        except (
            self.cognito.client.exceptions.CodeMismatchException,
            self.cognito.client.exceptions.ExpiredCodeException,
        ) as err:
            logger.warning(f"{error_msg}: code is expired or invalid")
            raise ConfirmationFailedException(
                "confirmation code is expired or invalid"
            ) from err
        except Exception as err:
            logger.error(f"{error_msg}: {err}")
            raise UnhandledException({error_msg}) from err

    def sign_up(self, username: str, password: str, email: str):
        cid = self.cognito.get_client_id()
        try:
            self.cognito.client.sign_up(
                ClientId=cid,
                Username=username,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )
        except self.cognito.client.exceptions.UsernameExistsException as err:
            logger.warning(
                f"failed to sign up user: username {username} already exists"
            )
            raise SignUpFailedException("username already exists") from err
        except self.cognito.client.exceptions.InvalidPasswordException as err:
            logger.warning("failed to sign up user: password is invalid")
            raise SignUpFailedException("password is invalid") from err
        except Exception as err:
            logger.error(f"failed to sign up {err}")
            raise UnhandledException("failed to sign up") from err


class SignUpServiceFactory:
    def __init__(self, settings):
        self.settings = settings

    def get(self) -> SignUpService:
        return CognitoSignUpService.from_settings(self.settings)
