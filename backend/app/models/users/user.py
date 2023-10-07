from typing import Optional, List

from pydantic import EmailStr, validator, root_validator
from sqlalchemy import Column, VARCHAR, BigInteger, Text
from sqlalchemy.dialects.postgresql import BYTEA
from sqlmodel import Field, SQLModel, Relationship

from backend.app.core.config import settings
from backend.app.models.common.common_attributes import CommonModelAttributes


class BaseUser(SQLModel):
    first_name: str = Field(sa_column=Column(VARCHAR(100)))
    last_name: str = Field(sa_column=Column(VARCHAR(100)))
    email: EmailStr
    phone: Optional[str] = Field(sa_column=Column(VARCHAR(16), nullable=True))


class UserIn(BaseUser):
    password: str = Field(sa_column=Column(VARCHAR(100)))
    repeat_password: str = Field(sa_column=Column(VARCHAR(100)))

    @validator("password", "repeat_password")
    def validate_password_length(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value

    @root_validator(pre=True)
    def check_password_match(cls, values):
        if values.get("password") != values.get("repeat_password"):
            raise ValueError("Passwords do not match")
        return values


class User(BaseUser, CommonModelAttributes, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": settings.db_schema}
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, index=True))
    password_hash: bytes = Field(sa_column=Column(BYTEA(255), nullable=False))

    books: Optional[List["Book"]] = Relationship(  # noqa
        sa_relationship_kwargs={
            "primaryjoin": "User.id==Book.added_by",
            "lazy": "joined",
            "uselist": True,
            # "overlaps": "books",
        }
    )

    class Config:
        arbitrary_types_allowed = True


class UserLogin(SQLModel):
    email: EmailStr
    password: str
