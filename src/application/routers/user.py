import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request
from pydantic import validate_email
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse, Response

from src.application.core import context
from src.application.core.api import forms
from src.application.core.config import get_settings
from src.application.core.db import User
from src.application.core.responses import JSONErrorResponse
from src.application.dependencies import AsyncDBSessionDepends
from src.application.services.auth.dependencies import ValidTokenDep
from src.application.services.aws import CognitoClient
from src.application.services.aws.exceptions import CognitoException
from src.application.services.crypto import EncryptorServiceFactory
from src.application.services.sign_up import SignUpServiceFactory
from src.application.tasks.user import sign_up_user
from src.application.utils.obfuscate import Obfuscator

from .dialog import router as dialog_router

router = APIRouter(prefix="/user", tags=["user"])

settings = get_settings()
logger = logging.getLogger()


@router.post("/sign-in", name="sign-in")
async def sign_in(response: Response, form: forms.SignInForm):
    cognito_wrapper = CognitoClient(settings.aws)
    cid = cognito_wrapper.get_client_id()
    try:
        auth_results = cognito_wrapper.auth_client(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": form.username, "PASSWORD": form.password},
            ClientId=cid,
        )
    except CognitoException as err:
        return JSONErrorResponse(str(err), status_code=status.HTTP_403_FORBIDDEN)

    response.set_cookie(
        settings.cookie_name,
        auth_results.access_token,
        expires=datetime.now(tz=timezone.utc)
        + timedelta(seconds=auth_results.expires_in),
    )
    return {"next": dialog_router.url_path_for("dialog")}


@router.post("/sign-up", name="do-sign-up")
async def sign_up(form: forms.SignUpForm, session: AsyncDBSessionDepends):
    exists = await User.async_exists(session, username=form.username, email=form.email)
    if exists:
        return JSONErrorResponse("username or email already exists", status_code=403)
    user = await User(username=form.username, email=form.email).async_create(session)
    encryptor = EncryptorServiceFactory(get_settings()).get()
    password = encryptor.encrypt(form.password)
    sign_up_user.delay(user.id, password)
    return {
        "next": f"{router.url_path_for('post-sign-up')}?email={form.email}&username={form.username}"
    }


@router.get("/sign-up", name="sign-up")
async def sign_up(request: Request):
    return context.templates.TemplateResponse(
        request=request,
        name="sign-up.html.j2",
        context={"sign_up_url": router.url_path_for("sign-up")},
    )


@router.post("/sign-up/confirm", name="confirm-sign-up")
async def confirm_sign_up(form: forms.CodeConfirmationForm):
    service = SignUpServiceFactory(settings.aws).get()
    service.confirm(form.username, form.code)
    return JSONResponse({"next": "/"})


@router.get("/sign-up/confirm", name="confirm-sign-up")
async def confirm_sign_up(username: str | None = None, code: str | None = None):
    service = SignUpServiceFactory(settings.aws).get()
    service.confirm(username, code)
    return RedirectResponse(url="/")


@router.get("/sign-up/post", name="post-sign-up")
async def post_sign_up(request: Request, email: str = "", username: str | None = None):
    if email:
        try:
            validate_email(email)
            email = Obfuscator(email).obfuscate_email()
        except ValueError:
            logger.info("got invalid email during verification")
            email = ""
    return context.templates.TemplateResponse(
        request=request,
        name="confirm-sign-up.html.j2",
        context={
            "email": email,
            "username": username,
            "confirm_sign_up_url": router.url_path_for("confirm-sign-up"),
        },
    )


@router.get("/sign-out", name="sign-out")
async def sign_out(token: ValidTokenDep):
    cognito = CognitoClient(settings.aws)
    cognito.sign_out(token)
    return
