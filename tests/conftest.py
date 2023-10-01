import asyncio
import os
from typing import Generator

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient

os.environ["APP_ENV"] = "test"

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from backend.main import get_application

    return get_application()


@pytest.fixture(scope="session")
async def initialized_app(app: FastAPI) -> FastAPI:
    async with LifespanManager(
        app, startup_timeout=20
    ):  # connecting to remote db taking more time hence overriding
        yield app


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_session(initialized_app: FastAPI):
    async with initialized_app.state.db_session() as session:
        yield session


@pytest.fixture(scope="session")
async def async_client(initialized_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=initialized_app,
        base_url="http://localhost:8000",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
