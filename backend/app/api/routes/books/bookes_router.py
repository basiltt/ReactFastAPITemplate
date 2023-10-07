from typing import Union

from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session
from starlette import status

from backend.app.api.routes.books.books_helper import (
    _add_book,
    _get_book,
    _get_user_books,
)
from backend.app.db.database import get_db
from backend.app.models.books.book import BookIn

router = APIRouter(prefix="/books", tags=["BOOKS"])


@router.post("/add-book", status_code=status.HTTP_200_OK)
async def add_book(
    book: BookIn,
    added_by: EmailStr,
    session: Union[AsyncSession, Session] = Depends(get_db),
):
    # """
    # route for adding a book
    # @return: BaseUser
    # """
    return await _add_book(book=book, added_by=added_by, session=session)


@router.get("/get-book", status_code=status.HTTP_200_OK)
async def get_book(
    book_name: str, session: Union[AsyncSession, Session] = Depends(get_db)
):
    # """
    # route for getting a book data
    # @return: Book
    # """
    return await _get_book(book_name=book_name, session=session)


@router.get("/get-user-books", status_code=status.HTTP_200_OK)
async def get_user_books(
    email: EmailStr, session: Union[AsyncSession, Session] = Depends(get_db)
):
    # """
    # route for getting all books owned by a user
    # @return: list of Book
    # """
    return await _get_user_books(email=email, session=session)
