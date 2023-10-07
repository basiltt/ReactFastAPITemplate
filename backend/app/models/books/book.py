from sqlalchemy import Column, VARCHAR, FLOAT, BigInteger, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from backend.app.core.config import settings

from backend.app.models.common.common_attributes import CommonModelAttributes
from backend.app.models.users.user import User


class BookIn(SQLModel):
    name: str = Field(sa_column=Column(VARCHAR(100)))
    price: float = Field(sa_column=Column(FLOAT))
    author: str = Field(sa_column=Column(VARCHAR(100)))


class Book(BookIn, CommonModelAttributes, table=True):
    __tablename__ = "books"
    __table_args__ = {"schema": settings.db_schema}
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, index=True))
    added_by: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey(f"{settings.db_schema}.users.id"),
            nullable=False,
            unique=False,
        )
    )

    # To create relationships simple way is available but to demonstrate the advanced usage using this way
    user: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Book.added_by==User.id",
            "lazy": "joined",
            "uselist": True,
            "viewonly": True,
            # "overlaps": "books",
        }
    )
