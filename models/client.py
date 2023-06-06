import random
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import event
from sqlalchemy.databases import postgres
from sqlalchemy.orm import declared_attr
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from models.base import UUIDModel


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"


user_role_type = postgres.ENUM(
    "admin",
    "manager",
    "user",
    name=f"user_role",
)


@event.listens_for(SQLModel.metadata, "before_create")
def _create_enums(metadata, conn, **kw):
    user_role_type.create(conn, checkfirst=True)


def generate_segment() -> int:
    return random.randint(0, 4)


class EditableUserBase(SQLModel):
    email: EmailStr = Field(
        nullable=True, index=True, sa_column_kwargs={"unique": True}
    )


class UserBase(EditableUserBase):
    is_active: bool = Field(default=True)
    role: str = Field(
        sa_column=Column("role", user_role_type, nullable=False),
        default=UserRole.user,
    )


class User(UUIDModel, UserBase):
    pass


class DBUser(User, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "serviceuser"

    hashed_password: Optional[str] = Field(nullable=False, index=True)
    link: "DBAudio" = Relationship(back_populates="user")


class AudioBase(SQLModel):
    link: str = Field(nullable=False, index=True)


class Audio(UUIDModel, AudioBase):
    pass


class DBAudio(Audio, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "audio"

    # Foreign keys
    user_id: UUID | None = Field(default=None, foreign_key="serviceuser.id")

    # Relations
    user: DBUser = Relationship(back_populates="link")
