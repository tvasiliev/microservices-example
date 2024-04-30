import asyncio
import json

from modules.app.app import create_app
from fastapi import Response
from starlette.responses import JSONResponse

from .config import config
from .rpc.server import TasksRPCServer
from .db import TasksDBManager


app = create_app(rpc_server=TasksRPCServer, config=config, database_manager=TasksDBManager)


@app.get("/ping-gateway")
async def ping_gateway_service() -> Response:
    """Checks availability of gateway microservice"""
    response = await app.rabbitmq_client.request(
        'gateway.ping',
        'tasks.gateway-request-callback',
        {'text': 'ping from tasks'}
    )

    return JSONResponse(json.loads(response.decode()))


@app.get("/ping-billing")
async def ping_billing_service() -> Response:
    """Checks availability of billing microservice"""
    response = await app.rabbitmq_client.request(
        'billing.ping',
        'tasks.billing-request-callback',
        {'text': 'ping from tasks'}
    )

    return JSONResponse(json.loads(response.decode()))
