from fastapi import APIRouter, Depends, HTTPException, status

from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

from app.core.security import (
    get_current_user,
    get_admin_user,
    hash_password,
)

router = APIRouter()


@router.get("/admin", response_model=list[UserRead])
def get_users(
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user),
):

    return session.exec(select(User)).all()


@router.get("/admin/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user),
):

    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post(
    "/admin",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user),
):

    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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

    return user


@router.put("/admin/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user),
):

    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    values = data.model_dump(exclude_unset=True)

    if "password" in values:
        values["password_hash"] = hash_password(
            values.pop("password")
        )

    for key, value in values.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user),
):

    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    session.delete(user)
    session.commit()


@router.get("/me", response_model=UserRead)
def get_me(
    current_user: User = Depends(get_current_user),
):

    return current_user


@router.put("/me", response_model=UserRead)
def update_me(
    data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    values = data.model_dump(exclude_unset=True)

    if "password" in values:
        values["password_hash"] = hash_password(
            values.pop("password")
        )

    for key, value in values.items():
        setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    session.delete(current_user)
    session.commit()