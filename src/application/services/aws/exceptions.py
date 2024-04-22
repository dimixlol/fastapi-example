from src.application.core.exceptions import UnhandledException


class AWSException(UnhandledException):
    pass


class CognitoException(AWSException):
    pass


class S3Exception(AWSException):
    pass
