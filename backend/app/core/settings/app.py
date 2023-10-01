import logging
import sys
from typing import Any, Dict, List, Tuple, Union

from loguru import logger
from pydantic import PostgresDsn

from backend.app.core.logging import InterceptHandler
from backend.app.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    debug: bool = True
    environment: str = "development"
    docs_url: str = "/docs"
    # docs_url: None = None
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FastAPI Skeleton Project"
    description = """
        FastAPI Skeleton Project - template repository for FastAPI projects.🚀
        """
    contact: dict = {
        "name": "RPA Support Team",
        "url": "https://home.hpe.com",
        "mail": "rpa_fin_support_team@hpe.com",
    }
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 10

    database_url: Union[PostgresDsn, str] = ""
    db_schema: str = "RBAC"
    max_db_pool_size: int = 10
    min_db_pool_size: int = 5
    pool_recycle: int = 3600
    db_pool_pre_ping: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_key_expiry: int = 120
    secret_key: str = "aa9873796bd5a9ac78edb1123aff667e45mm92861c15c3568d5ff036aa7420f0"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 300
    client_id: str = "SomeClintID"
    client_secret: str = "SomeClientSecret"
    redirect_uri: str = "https://d2wg10130.s10.its.hpecorp.net:50038/q2o/callback"
    api_prefix: str = "/api"
    jwt_token_prefix: str = "Token"
    allowed_hosts: List[str] = ["*"]
    o365_client_id: str = ""
    o365_client_secret: str = ""
    email_sender: str = ""
    smtp_server: str = "smtp3.hpe.com"
    smtp_port: int = 25
    send_alerts: bool = False
    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")
    test_user: dict = {
        "country": "IN",
        "uid": "basil.tt@hpe.com",
        "sub": "basil.tt@hpe.com",
        "hpBusinessUnit": "Controller ship Finance",
        "hpeSpinCompany": "Houston",
        "hpBusinessRegion": "Worldwide",
        "name": "Basil T T",
        "given_name": "Basil",
        "locale": "Bangalore",
        "family_name": "T T",
        "email": "basil.tt@hpe.com",
        "employeeNumber": "60156119",
    }

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
            "description": self.description,
            "contact": self.contact,
        }

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]

        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])
