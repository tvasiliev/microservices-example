import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.rpc.client import RPCClient

from .utils import add_task_to_loop


def create_app(rpc_server, config) -> FastAPI:
    """Application instance creation"""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
        app.rabbitmq_client = RPCClient(broker_url=config.RABBITMQ_URL)
        add_task_to_loop(app.rabbitmq_client.connect())

        app.rabbitmq_server = rpc_server(broker_url=config.RABBITMQ_URL)
        add_task_to_loop(app.rabbitmq_server.listen())

        yield

        await app.rabbitmq_client.close()

    app = FastAPI(title=config.PROJECT_NAME, version="0.1", docs_url="/api/docs", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.templates = Jinja2Templates(directory="app/templates")
    return app
