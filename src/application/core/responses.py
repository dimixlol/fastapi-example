from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from src.application.core.exceptions import UnhandledException


class JSONErrorResponse(JSONResponse):
    def __init__(
        self, detail, status_code: int = status.HTTP_400_BAD_REQUEST, **kwargs
    ):
        kwargs.setdefault("headers", {"content-type": "application/problem+json"})
        super().__init__(content=detail, status_code=status_code, **kwargs)

    @classmethod
    def from_exc(cls, exc: Exception, status_code: int = None, **kwargs):
        detail = str(exc)
        if isinstance(exc, (UnhandledException, HTTPException)):
            detail = "An unexpected error occurred"

        if status_code is None:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            if code := getattr(exc, "status_code", None):
                status_code = code

        return cls(detail={"detail": detail}, status_code=status_code, **kwargs)
