import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.rpc.client import RPCClient

from .config import config
from .db import recreate_db


def create_app() -> FastAPI:
    """Application instance creation"""
    app = FastAPI(title=config.PROJECT_NAME, version="0.1", docs_url="/api/docs")
    app.rabbitmq_client = RPCClient(broker_url=config.RABBITMQ_URL)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.templates = Jinja2Templates(directory="app/templates")
    recreate_db()
    return app
