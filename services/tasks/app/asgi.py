import asyncio
import json

from modules.app.app import create_app
from fastapi import Response
from starlette.responses import JSONResponse

from .config import config
from .rpc.server import TasksRPCServer


app = create_app(rpc_server=TasksRPCServer, config=config)


@app.get("/ping-gateway")
async def ping_task_service() -> Response:
    """Checks availability of gateway microservice"""
    callback_queue_name = 'tasks.gateway-request-callback'

    await app.rabbitmq_client.consume(callback_queue_name)
    response = await app.rabbitmq_client.call('gateway.ping', callback_queue_name, {'text': 'ping from tasks'})

    return JSONResponse(json.loads(response.decode()))


@app.get("/ping-billing")
async def ping_billing_service() -> Response:
    """Checks availability of billing microservice"""
    callback_queue_name = 'tasks.billing-request-callback'

    await app.rabbitmq_client.consume(callback_queue_name)
    response = await app.rabbitmq_client.call('billing.ping', callback_queue_name, {'text': 'ping from tasks'})

    return JSONResponse(json.loads(response.decode()))
