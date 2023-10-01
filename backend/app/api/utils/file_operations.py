import os

from fastapi import FastAPI
from loguru import logger

#  get current working directory
cwd = os.getcwd()
UPLOADS_PATH = [
    os.path.join(cwd, "backend", "files", "media_data"),
    os.path.join(cwd, "backend", "files", "product_data"),
    os.path.join(cwd, "backend", "files", "sfdc_data"),
    os.path.join(cwd, "backend", "files", "support_data"),
]


async def create_initial_directories(app: FastAPI) -> None:
    """Create initial directories."""
    logger.info("Creating initial directories")
    for path in UPLOADS_PATH:
        if not os.path.exists(path):
            os.makedirs(path)
    logger.info("Initial directories created")
