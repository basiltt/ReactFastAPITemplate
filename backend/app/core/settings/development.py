import logging

from backend.app.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True

    title: str = "FastAPI Skeleton Project - Dev"
    max_db_pool_size: int = 2
    min_db_pool_size: int = 4
    environment = "development"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = "dev.env"
