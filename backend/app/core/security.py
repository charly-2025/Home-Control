import bcrypt

from fastapi import Cookie, Depends, HTTPException, status

from sqlmodel import Session

from app.auth.jwt import decode_token
from app.database import get_session
from app.models import User
from app.core.roles import UserRole



def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(),
    ).decode()


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        password_hash.encode(),
    )


def get_current_user(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session),
):

    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    payload = decode_token(access_token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = session.get(
        User,
        int(payload["sub"]),
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account disabled",
        )

    return user

def get_admin_user(
    user: User = Depends(get_current_user),
):

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return user