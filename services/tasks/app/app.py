import asyncio

from fastapi import FastAPI

from .config import config


def create_app() -> FastAPI:
    """Application instance creation"""
    app = FastAPI(title=config.PROJECT_NAME, version="0.1", docs_url="/api")
    return app
