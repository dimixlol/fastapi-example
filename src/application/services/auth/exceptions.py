from src.application.core.exceptions import TechnicalException


class JWTHeaderVerificationFailed(TechnicalException):
    pass


class JWTTokenVerificationFailed(TechnicalException):
    pass
