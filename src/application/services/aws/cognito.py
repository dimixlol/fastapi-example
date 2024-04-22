import boto3
import requests
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal

from src.application.core.config import AWSSettings

from .exceptions import CognitoException


class CognitoAuthResult(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: str
    id_token: str
    model_config = ConfigDict(alias_generator=to_pascal)


class CognitoJWKS(BaseModel):
    kty: str
    alg: str
    use: str
    kid: str
    e: str
    n: str


class CognitoClient:
    __jwks_cache: dict[str, CognitoJWKS] = {}
    _user_pool_id: str = ""
    _user_client_id: str = ""

    def __init__(self, settings: AWSSettings):
        self.settings = settings
        self.client = boto3.client(
            "cognito-idp",
            region_name=settings.region,
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key,
            endpoint_url=settings.endpoint_url,
        )

    def get_client_id(self) -> str:
        if not self._user_client_id:
            pool = self.get_user_pool_id()
            clients = self.client.list_user_pool_clients(UserPoolId=pool)
            try:
                self._user_client_id = clients["UserPoolClients"][0]["ClientId"]
            except KeyError as err:
                raise CognitoException("Invalid response from cognito") from err
        return self._user_client_id

    def get_user_pool_id(self) -> str:
        if not self._user_pool_id:
            pools = self.client.list_user_pools(MaxResults=100)
            try:
                self._user_pool_id = pools["UserPools"][0]["Id"]
            except KeyError as err:
                raise CognitoException("Invalid response from cognito") from err
        return self._user_pool_id

    def auth_client(self, **kwargs):
        try:
            response = self.client.initiate_auth(**kwargs)
        except (
            self.client.exceptions.NotAuthorizedException,
            self.client.exceptions.UserNotFoundException,
        ) as err:
            raise CognitoException("invalid username or password") from err
        except self.client.exceptions.UserNotConfirmedException as err:
            raise CognitoException("user not confirmed") from err
        return CognitoAuthResult(**response["AuthenticationResult"])

    def get_pool_issuer_url(self):
        return f"{self.settings.endpoint_url}/{self.get_user_pool_id()}"

    def get_pool_jwks(self):
        if self._user_pool_id in self.__jwks_cache:
            return self.__jwks_cache[self._user_pool_id]
        data = requests.get(
            f"{self.get_pool_issuer_url()}/.well-known/jwks.json", timeout=10
        )
        jwks = CognitoJWKS(**data.json()["keys"][0])
        self.__jwks_cache[self._user_pool_id] = jwks
        return jwks

    def sign_out(self, token: str):
        return self.client.global_sign_out(AccessToken=token)
