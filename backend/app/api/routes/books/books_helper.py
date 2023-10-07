from typing import Union

from fastapi import HTTPException
from pydantic import EmailStr
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.db.database import get_from_db, update_db
from backend.app.models.books.book import BookIn, Book
from backend.app.models.users.user import User


async def _add_book(
    book: BookIn, added_by: EmailStr, session: Union[AsyncSession, Session]
):
    book_db = await get_from_db(
        session=session, instance=Book, multiple=False, name=book.name
    )
    if book_db is not None:
        raise HTTPException(status_code=400, detail=f"Book {book.name} already exists")
    added_user = await get_from_db(
        session=session, instance=User, multiple=False, email=added_by
    )
    if added_user is None:
        raise HTTPException(status_code=400, detail=f"User {added_by} does not exist")
    new_book = Book(
        name=book.name, price=book.price, author=book.author, added_by=added_user.id
    )
    book_db = await update_db(session, new_book, refresh_data=True)
    return book_db


async def _get_book(book_name: str, session: Union[AsyncSession, Session]):
    book_db = await get_from_db(
        session=session, instance=Book, multiple=False, name=book_name
    )
    if book_db is None:
        raise HTTPException(status_code=404, detail=f"Book {book_name} does not exist")
    return book_db


async def _get_user_books(email: EmailStr, session: Union[AsyncSession, Session]):
    user_db = await get_from_db(
        session=session, instance=User, multiple=False, email=email
    )
    if user_db is None:
        raise HTTPException(status_code=404, detail=f"User {email} does not exist")
    # book_db = await get_from_db(session=session, instance=Book, multiple=True, added_by=user_db.id)
    return user_db.books
