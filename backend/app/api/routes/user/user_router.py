from typing import Union

from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from backend.app.api.routes.user.user_helper import _sign_up, _sign_in
from backend.app.db.database import get_db
from backend.app.models.users.user import BaseUser, UserIn, UserLogin

router = APIRouter(prefix="/users", tags=["USERS"])


@router.post("/sign-up", status_code=status.HTTP_201_CREATED, response_model=BaseUser)
async def sign_up(
    user: UserIn, session: Union[AsyncSession, Session] = Depends(get_db)
):
    # """
    # route for creating a users
    # @return: BaseUser
    # """
    return await _sign_up(user=user, session=session)


@router.post("/sign-in", status_code=status.HTTP_200_OK)
async def sign_in(
    user: UserLogin, session: Union[AsyncSession, Session] = Depends(get_db)
):
    # """
    # route for signing in a users
    # @return: BaseUser
    # """
    return await _sign_in(user=user, session=session)
