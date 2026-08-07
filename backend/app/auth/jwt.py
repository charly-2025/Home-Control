from datetime import UTC, datetime, timedelta
import os
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not defined in the environment")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30)
)


def create_access_token(user_id: int) -> str:

    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": datetime.now(UTC),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_refresh_token(user_id: int) -> str:

    expire = datetime.now(UTC) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": datetime.now(UTC),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(
    token: str,
) -> dict[str, Any] | None:

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except InvalidTokenError:
        return None


def is_access_token(
    token: str,
) -> bool:

    payload = decode_token(token)

    return (
        payload is not None
        and payload.get("type") == "access"
    )


def is_refresh_token(
    token: str,
) -> bool:

    payload = decode_token(token)

    return (
        payload is not None
        and payload.get("type") == "refresh"
    )


def get_user_id(
    token: str,
) -> int | None:

    payload = decode_token(token)

    if payload is None:
        return None

    try:
        return int(payload["sub"])

    except (KeyError, ValueError):
        return None