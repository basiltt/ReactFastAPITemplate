from fastapi import FastAPI
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlmodel import SQLModel

from backend.app.core.settings.app import AppSettings

# from backend.app.db.initial_data_loader import load_initial_data_to_db

# DROP_TABLES = False
DROP_TABLES = True

# from backend.app.db.initial_data_loader import load_initial_data_to_db

LOAD_INITIAL_DATA = False
# LOAD_INITIAL_DATA = True

DROP_TABLES = False
# DROP_TABLES = True

settings_object = None


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    global settings_object
    settings_object = settings
    logger.info("Connecting to {0}", repr(settings.database_url))
    is_driver_async = settings.database_url.startswith("postgresql+asyncpg")
    app.state.settings = settings
    if is_driver_async:
        app.state.engine = create_async_engine(
            settings.database_url,
            pool_size=settings.max_db_pool_size,
            pool_recycle=settings.pool_recycle,
            pool_pre_ping=settings.db_pool_pre_ping,
            poolclass=QueuePool,
            future=True,
            echo=False,
        )
        app.state.db_session = sessionmaker(
            app.state.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with app.state.engine.begin() as conn:
            if DROP_TABLES:
                await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
    else:
        app.state.engine = create_engine(
            settings.database_url,
            pool_size=settings.max_db_pool_size,
            pool_recycle=settings.pool_recycle,
            pool_pre_ping=settings.db_pool_pre_ping,
            poolclass=QueuePool,
            future=True,
            echo=False,
        )
        app.state.db_session = sessionmaker(app.state.engine, expire_on_commit=False)
        if DROP_TABLES:
            SQLModel.metadata.drop_all(bind=app.state.engine)
        SQLModel.metadata.create_all(bind=app.state.engine)
        # if LOAD_INITIAL_DATA:
        #     await load_initial_data_to_db(app.state.db_session())
    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")
    # Dropping all tables in test environment on exit
    if app.state.settings.environment == "test":
        logger.info("Dropping all tables in test environment")
        is_driver_async = app.state.settings.database_url.startswith(
            "postgresql+asyncpg"
        )
        if is_driver_async:
            async with app.state.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.drop_all)
        else:
            SQLModel.metadata.drop_all(bind=app.state.engine)
        logger.info("All tables dropped")

    async def __aenter__(self):
        async with app.state.db_session() as session:
            await session.close()
            await app.state.engine.dispose()

    logger.info("Connection closed")
