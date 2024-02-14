import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.rpc.client import RPCClient
from modules.rpc.utils import create_connection

from .utils import add_task_to_loop


def create_app(rpc_server, config) -> FastAPI:
    """Application instance creation"""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
        """FastAPI app lifespan with RabbitMQ connection management"""
        rabbitmq_connection = await create_connection(broker_url=config.RABBITMQ_URL)

        app.rabbitmq_client = RPCClient(rabbitmq_connection)
        await app.rabbitmq_client.create_channel()

        app.rabbitmq_server = rpc_server(rabbitmq_connection)
        await app.rabbitmq_server.create_channel()

        add_task_to_loop(app.rabbitmq_server.listen())

        yield

        # gracefully closing connection
        await app.rabbitmq_client.close_channel()
        await app.rabbitmq_server.close_channel()
        await rabbitmq_connection.close()

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
