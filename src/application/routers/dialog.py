import logging
from uuid import uuid4

from fastapi import APIRouter
from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.application.core import context
from src.application.core.api import forms
from src.application.core.db import Message
from src.application.dependencies import AsyncDBSessionDepends
from src.application.services.auth.dependencies import CurrentUserDep, get_current_user
from src.application.tasks.dialog import upload_to_s3

router = APIRouter(prefix="/dialog", tags=["dialog"])


logger = logging.getLogger()


@router.get("/", name="dialog")
async def dialog(request: Request, current_user: CurrentUserDep):
    return context.templates.TemplateResponse(
        request=request, name="dialog.html.j2", context={"ws_link": "/dialog/ws"}
    )


@router.websocket("/ws/{token}", name="ws")
async def ws(websocket: WebSocket, token: str, session: AsyncDBSessionDepends):
    await websocket.accept()
    user = await get_current_user(session, token=token)
    logger.info(f"connected user {user.username}")
    try:
        while True:
            data = await websocket.receive_json()
            form = forms.DialogForm(**data)
            message_id = uuid4()
            message = Message(
                id=message_id, path=Message.compose_path(message_id), user_id=user.id
            )
            await message.async_create(session)
            result = upload_to_s3.delay(message_id, form.message)
            resolved = result.get()
            await websocket.send_json(resolved)
    except WebSocketDisconnect:
        await websocket.close()
