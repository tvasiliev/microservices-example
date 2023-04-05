import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import config
from .db import recreate_db


def create_app() -> FastAPI:
    """Application instance creation"""
    app = FastAPI(title=config.PROJECT_NAME, version="0.1", docs_url="/api")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.templates = Jinja2Templates(directory="app/templates")
    recreate_db()
    return app
