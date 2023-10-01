import logging

from pydantic import SecretStr

from backend.app.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True
    title: str = "FastAPI Skeleton Project - Test"
    secret_key: SecretStr = SecretStr("test_secret")
    max_db_pool_size: int = 10
    min_db_pool_size: int = 5
    pool_recycle: int = 3600
    logging_level: int = logging.DEBUG
    environment = "test"

    class Config(AppSettings.Config):
        env_file = "test.env"
