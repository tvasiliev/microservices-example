import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modules.rabbitmq.client import create_connection

from .utils import add_task_to_loop

if TYPE_CHECKING:
    from modules.db import DBManager
    from modules.rabbitmq.rpc.server import RPCServer
    from modules.rabbitmq.rpc.client import RPCClient
    from pydantic import BaseModel


def create_app(rpc_server: 'RPCServer', rpc_client: 'RPCClient', config: 'BaseModel', database_manager: 'DBManager') -> FastAPI:
    """Application instance creation"""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
        """FastAPI app lifespan with RabbitMQ connection management"""
        app.db_manager = database_manager(config.POSTGRES_URL)
        app.db_manager.add_absent_data_to_db()

        rmq_input_connection = await create_connection(broker_url=config.RABBITMQ_URL)
        rmq_output_connection = await create_connection(broker_url=config.RABBITMQ_URL)
        # separate connections help to read messages when flow control regulates connetion with high amount of sendings

        app.rabbitmq_client = rpc_client(
            rmq_input_connection,
            rmq_output_connection,
            config.CLIENT_PUBLISH_RETRIES
        )
        await app.rabbitmq_client.open_channels()

        app.rabbitmq_server = rpc_server(
            rmq_input_connection,
            rmq_output_connection,
            config.SERVER_PUBLISH_RETRIES
        )
        await app.rabbitmq_server.open_channels()

        add_task_to_loop(app.rabbitmq_server.listen())
        # listens on the declared queues infinitely

        yield

        # gracefully closing channels and connections
        await app.rabbitmq_client.close_channels()
        await app.rabbitmq_server.close_channels()
        await rmq_input_connection.close()
        await rmq_output_connection.close()

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
