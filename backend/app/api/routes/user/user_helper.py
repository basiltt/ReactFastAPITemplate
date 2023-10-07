from typing import Union

import bcrypt
from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.core.config import settings
from backend.app.db.database import get_from_db, update_db
from backend.app.models.users.user import User, UserIn, UserLogin, BaseUser


async def hash_password(password: str):
    # Generate a random salt
    salt = bcrypt.gensalt()

    # Hash the password using the salt and the secret key
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"), salt + settings.secret_key.encode("utf-8")
    )

    return hashed_password


def validate_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Validate a plain password against a hashed password.
    Returns True if the plain password matches the hashed password, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


async def _sign_up(user: UserIn, session: Union[Session, AsyncSession]):
    used_db = await get_from_db(
        session=session, instance=User, multiple=False, email=user.email
    )
    if used_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = await hash_password(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
    )
    print(f"new_user: {new_user}")
    user_db = await update_db(session, new_user, refresh_data=True)
    return user_db


async def _sign_in(user: UserLogin, session: Union[Session, AsyncSession]) -> BaseUser:
    user_db = await get_from_db(
        session=session, instance=User, multiple=False, email=user.email
    )
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")
    if not validate_password(user.password, user_db.password_hash):
        raise HTTPException(status_code=400, detail="Invalid password")
    return user_db
