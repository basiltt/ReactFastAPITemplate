from functools import lru_cache
from typing import Dict, Type

from backend.app.core.settings.app import AppSettings
from backend.app.core.settings.base import AppEnvTypes, BaseAppSettings
from backend.app.core.settings.development import DevAppSettings
from backend.app.core.settings.production import ProdAppSettings
from backend.app.core.settings.test import TestAppSettings

environments: Dict[AppEnvTypes, Type[AppSettings]] = {
    AppEnvTypes.dev: DevAppSettings,
    AppEnvTypes.prod: ProdAppSettings,
    AppEnvTypes.test: TestAppSettings,
}


# @lru_cache
def get_app_settings() -> AppSettings:
    app_env = BaseAppSettings().app_env
    config = environments[app_env]
    return config()


settings = get_app_settings()
