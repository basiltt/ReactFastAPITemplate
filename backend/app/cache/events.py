import aioredis
from fastapi import FastAPI
from loguru import logger

from backend.app.core.settings.app import AppSettings


async def connect_to_cache(app: FastAPI, settings: AppSettings):
    redis_url: str = f"redis://{settings.redis_host}:{settings.redis_port}"
    logger.info("Connecting to Redis Cache {0}", repr(redis_url))
    async with aioredis.from_url(
        redis_url, encoding="utf8", decode_responses=True
    ) as pool:
        app.state.cache = aioredis.Redis(connection_pool=pool).connection_pool
    logger.info("Redis Cache Connection established")


async def close_cache_connection(app: FastAPI):
    logger.info("Closing connection to Redis Cache")

    await app.state.cache.close()

    logger.info("Connection to Redis Cache closed")
