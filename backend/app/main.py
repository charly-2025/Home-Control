from contextlib import asynccontextmanager

import asyncio
from fastapi import FastAPI
from sqlmodel import SQLModel

from .database import engine
from .database import wait_for_database

from .mqtt import mqtt_client

from .services.device_manager import device_manager
from .websocket import websocket_manager

from .routes import auth
from .routes import users
from .routes import devices
from .routes import websocket

@asynccontextmanager
async def lifespan(app: FastAPI):

    wait_for_database()
    SQLModel.metadata.create_all(engine)

    mqtt_client.wait_for_connection()
    
    websocket_manager.set_loop(
        asyncio.get_running_loop()
    )

    yield

    mqtt_client.disconnect()


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"],
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
)

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"],
)

app.include_router(
    devices.router,
    prefix="/api/devices",
    tags=["Devices"],
)


@app.get("/api/")
def root():
    return {
        "message": "Home Control API"
    }