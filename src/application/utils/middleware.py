import logging

from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.application.core.responses import JSONErrorResponse

logger = logging.getLogger()


async def convert_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unexpected error occurred: {exc}", exc_info=exc)
        return JSONErrorResponse.from_exc(exc)


async def auth_failed_exception_handler(*_, **__):
    return RedirectResponse(url="/")
