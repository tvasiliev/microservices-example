import asyncio
import json

from modules.app.app import create_app
from fastapi import Response
from starlette.responses import JSONResponse

from .config import config
from .rpc.server import BillingRPCServer
from .rpc.client import BillingRPCClient
from .db import BillingDBManager


app = create_app(rpc_server=BillingRPCServer, rpc_client=BillingRPCClient, config=config, database_manager=BillingDBManager)


@app.get("/ping-gateway")
async def ping_gateway_service() -> Response:
    """Checks availability of gateway microservice"""
    response = await app.rabbitmq_client.request(
        routing_key='gateway.request',
        message_body={'text': 'ping from billing'}
    )

    return JSONResponse(json.loads(response.decode()))


@app.get("/ping-tasks")
async def ping_tasks_service() -> Response:
    """Checks availability of tasks microservice"""
    response = await app.rabbitmq_client.request(
        routing_key='tasks.request',
        message_body={'text': 'ping from billing'}
    )

    return JSONResponse(json.loads(response.decode()))
