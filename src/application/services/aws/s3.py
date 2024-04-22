import boto3

from src.application.core.config import AWSSettings


class S3Client:
    _bucket: str

    def __init__(self, settings: AWSSettings):
        self._bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key,
            region_name=settings.region,
            endpoint_url=settings.endpoint_url,
        )

    def upload(self, key: str, data: str):
        return self.client.put_object(Bucket=self._bucket, Key=key, Body=data)

    def get_presigned_url(self, key: str) -> str:
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self._bucket, "Key": key}
        )
