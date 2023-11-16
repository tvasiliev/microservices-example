
import asyncio
import json
import uuid
from typing import MutableMapping

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)


class RPCClient:
    """Client for RPC RabbitMQ calls"""

    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue

    def __init__(self, queue_name: str, broker_url: str) -> None:
        self.queue_name = queue_name
        self.broker_url = broker_url
        self.futures: MutableMapping[str, asyncio.Future] = {}

    async def connect(self):
        """Creates connection and sets callback queue"""
        self.connection = await connect(self.broker_url)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)

    async def on_response(self, message: AbstractIncomingMessage) -> None:
        """Handles response"""
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, **kwargs):
        """Sends message to RPC server"""
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(kwargs).encode("utf-8"),
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=self.queue_name,
            timeout=30
        )

        return await future
