import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSSettings(BaseSettings):
    region: str = "us-east-1"
    access_key_id: str = "test"
    secret_access_key: str = "test"
    endpoint_url: str = "http://localhost.localstack.cloud:4566"
    s3_bucket: str = "bucket-1"
    cognito_pool: str = "pool-1"
    cognito_pool_client: str = "client-1"
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'local')}",
        env_prefix="AWS_",
        validate_default=False,
        extra="allow",
    )
