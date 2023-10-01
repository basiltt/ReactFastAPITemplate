from os import chdir, path
from pathlib import Path, PurePath

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from backend.app.api.routes.api import router as api_router
from backend.app.api.utils.hpe_oauth import HpaOauth
from backend.app.core.config import get_app_settings
from backend.app.core.events import create_start_app_handler, create_stop_app_handler
from backend.app.errors.http_error import http_error_handler
from backend.app.errors.validation_error import http422_error_handler

# Setting script directory as working directory
chdir(path.dirname(path.abspath(__file__)))

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
STATICFILES_DIRS = FRONTEND_DIR / "build/static"

settings = get_app_settings()


def get_application() -> FastAPI:
    settings.configure_logging()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = get_application()

#  Mounting static files and adding session middleware only in production
# if settings.environment == "production" or settings.environment == "development":
# if settings.environment == "production":
#     app.mount(
#         "/static",
#         StaticFiles(directory=PurePath(STATICFILES_DIRS), html=True),
#         name="static",
#     )

# hpe_oauth_config = {
#     "client_id": settings.client_id,
#     "client_secret": settings.client_secret,
#     "redirect_uri": settings.redirect_uri,
# }
#
# hpe_oauth_client = HpaOauth(config=hpe_oauth_config)
