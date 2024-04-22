from starlette.requests import Request

from src.application.core.config import Settings


class CookieExtractor:
    def __init__(self, settings: Settings):
        self.cookie_name = settings.cookie_name

    def __call__(self, req: Request) -> str:
        return req.cookies.get(self.cookie_name, "")
