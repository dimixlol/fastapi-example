from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.application.core import context
from src.application.core.exceptions import UnauthorizedException
from src.application.routers import DIALOG_ROUTER, USER_ROUTER
from src.application.services.auth import CookieExtractor, JWTValidator
from src.application.services.aws import CognitoClient
from src.application.utils import middleware

app = FastAPI(title=context.settings.project_name)
app.middleware("http")(middleware.convert_exceptions)
app.add_exception_handler(
    UnauthorizedException, middleware.auth_failed_exception_handler
)
app.mount("/static", context.static, name="static")
app.include_router(USER_ROUTER)
app.include_router(DIALOG_ROUTER)


@app.get("/", name="root")
async def root(request: Request):
    token = CookieExtractor(context.settings)(request)
    validator = JWTValidator(CognitoClient(context.settings.aws))
    if validator.is_valid(token=token, raise_exception=False):
        return RedirectResponse(url="/dialog")
    return context.templates.TemplateResponse(
        request=request,
        name="index.html.j2",
        context={
            "sign_in_url": app.url_path_for("sign-in"),
            "sign_up_url": app.url_path_for("sign-up"),
        },
    )
