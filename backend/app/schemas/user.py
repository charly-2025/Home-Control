from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel

from ..core.roles import UserRole


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserCreate(SQLModel):
    email: EmailStr
    password: str

    first_name: str
    last_name: str


class UserUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserRead(SQLModel):
    id: int

    first_name: str
    last_name: str

    email: EmailStr

    role: UserRole

    is_active: bool
    is_verified: bool

    created_at: datetime
    updated_at: datetime
