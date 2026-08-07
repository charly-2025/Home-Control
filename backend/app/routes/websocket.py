from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi import status

from sqlmodel import Session

from app.auth.jwt import decode_token
from app.database import engine
from app.models import User
from app.websocket import websocket_manager

router = APIRouter()


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
):

    access_token = websocket.cookies.get("access_token")

    if access_token is None:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
        )
        return

    payload = decode_token(access_token)

    if payload is None or payload.get("type") != "access":
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
        )
        return

    with Session(engine) as session:

        user = session.get(
            User,
            int(payload["sub"]),
        )

        if user is None or not user.is_active:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
            )
            return

    await websocket_manager.connect(websocket)

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)