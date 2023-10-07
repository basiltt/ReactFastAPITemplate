from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.requests import Request


async def get_db(request: Request) -> Union[AsyncSession, Session]:
    settings = request.app.state.settings
    is_driver_async = settings.database_url.startswith("postgresql+asyncpg")
    if is_driver_async:
        async with request.app.state.db_session() as session:
            yield session
    else:
        with request.app.state.db_session() as session:
            yield session


async def update_db(
    session: Union[Session, AsyncSession], instance, refresh_data=False
) -> None:
    is_driver_async = isinstance(session, AsyncSession)
    if isinstance(instance, list):
        if is_driver_async:
            try:
                session.bulk_save_objects(instance)
                await session.commit()
            except Exception as e:
                print(e)
                await session.rollback()
        else:
            try:
                session.bulk_save_objects(instance)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
    else:
        if is_driver_async:
            try:
                session.add(instance)
                await session.commit()
                if refresh_data:
                    await session.refresh(instance)
            except Exception as e:
                print(e)
                await session.rollback()
        else:
            try:
                session.add(instance)
                session.commit()
                if refresh_data:
                    session.refresh(instance)
            except Exception as e:
                print(e)
                session.rollback()
    print("Updated database")


# async def get_from_db(
#     session: Union[Session, AsyncSession], instance, multiple=True, **kwargs
# ) -> None:
#     is_driver_async = isinstance(session, AsyncSession)
#     statement = select(instance).filter_by(**kwargs)
#     if is_driver_async:
#         if multiple:
#             output = await session.scalars(statement).all()
#         else:
#             output = await session.scalars(statement).first()
#     else:
#         if multiple:
#             output = session.scalars(statement).all()
#         else:
#             output = session.scalars(statement).first()
#     return output


async def get_from_db(
    session: Union[Session, AsyncSession], instance, multiple=True, **kwargs
):
    is_driver_async = isinstance(session, AsyncSession)
    statement = select(instance).filter_by(**kwargs)

    if is_driver_async:
        result = await session.execute(statement)
    else:
        result = session.execute(statement)

    if multiple:
        output = (
            [row[0] for row in result] if is_driver_async else result.scalars().all()
        )
    else:
        output = result.scalar() if is_driver_async else result.scalar()

    return output
