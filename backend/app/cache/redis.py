import json
from datetime import date, datetime
from json import JSONEncoder

from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from backend.app.core.config import get_app_settings


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


class RedisCache:
    @staticmethod
    async def set(key, value, request: Request):
        settings = get_app_settings()
        data = json.dumps(value, indent=4, sort_keys=False, cls=DateTimeEncoder)
        try:
            await request.app.state.cache.set(key, data)
            await request.app.state.cache.expire(
                name=key, time=settings.redis_key_expiry
            )
        except ConnectionError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Redis connectivity failed",
            )

    @staticmethod
    async def get(key, request: Request):
        try:
            data = await request.app.state.cache.get(key)
            if data:
                return json.loads(data)
            return None
        except ConnectionError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Redis connectivity failed",
            )


redis_cache = RedisCache()
