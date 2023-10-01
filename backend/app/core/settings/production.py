from backend.app.core.settings.app import AppSettings


class ProdAppSettings(AppSettings):
    title: str = "Q2O"
    max_db_pool_size: int = 32
    min_db_pool_size: int = 128
    pool_recycle: int = 3600
    environment = "production"

    class Config(AppSettings.Config):
        env_file = "prod.env"
