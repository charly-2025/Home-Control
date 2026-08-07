from fastapi import APIRouter, Cookie, Depends, HTTPException, Response

from sqlmodel import Session, select

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    get_user_id,
    is_refresh_token,
)

from app.database import get_session
from app.models import User
from app.schemas.user import UserLogin, UserCreate
from app.core.security import (
    verify_password,
    hash_password,
)

router = APIRouter()

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"

ACCESS_COOKIE_MAX_AGE = 60 * 15
REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 30


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=False,  # True en production (HTTPS)
        samesite="lax",
        max_age=ACCESS_COOKIE_MAX_AGE,
        path="/",
    )

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=False,  # True en production (HTTPS)
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/",
    )


def clear_auth_cookies(
    response: Response,
) -> None:

    response.delete_cookie(
        ACCESS_COOKIE_NAME,
        path="/",
    )

    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path="/",
    )


@router.post("/login")
def login(
    data: UserLogin,
    response: Response,
    session: Session = Depends(get_session),
):

    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account disabled",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    set_auth_cookies(
        response,
        access_token,
        refresh_token,
    )

    return {
        "message": "Login successful",
    }


@router.post("/register")
def register(
    data: UserCreate,
    response: Response,
    session: Session = Depends(get_session),
):

    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    set_auth_cookies(
        response,
        access_token,
        refresh_token,
    )

    return {
        "message": "Account created",
    }


@router.post("/logout")
def logout(
    response: Response,
):

    clear_auth_cookies(response)

    return {
        "message": "Logout successful",
    }


@router.post("/refresh")
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session),
):

    if refresh_token is None:
        raise HTTPException(
            status_code=401,
            detail="Missing refresh token",
        )

    if not is_refresh_token(refresh_token):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    user_id = get_user_id(refresh_token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    user = session.get(
        User,
        user_id,
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

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    set_auth_cookies(
        response,
        new_access_token,
        new_refresh_token,
    )

    return {
        "message": "Token refreshed",
    }