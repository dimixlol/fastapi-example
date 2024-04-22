from starlette import status


class TechnicalException(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST


class BusinessException(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST


class UnhandledException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR


class UnauthorizedException(TechnicalException):
    status_code = status.HTTP_401_UNAUTHORIZED
