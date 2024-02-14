
import asyncio
import json
import uuid
from typing import MutableMapping, Awaitable

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)


class RPCClient:
    """Client for RPC RabbitMQ calls"""

    _connection: AbstractConnection
    _channel: AbstractChannel
    _callback_queue: AbstractQueue

    def __init__(self, broker_url: str) -> None:
        self._broker_url = broker_url
        self._futures: MutableMapping[str, asyncio.Future] = {}

    async def connect(self) -> Awaitable[None]:
        self._connection = await connect(self._broker_url)
        self._channel = await self._connection.channel()

    async def close(self) -> Awaitable[None]:
        self._channel.close()
        await self._connection.close()

    async def consume(self, queue_name: str) -> Awaitable[None]:
        """Consumes certain queue"""
        queue = await self._channel.declare_queue(name=queue_name, exclusive=True)
        await queue.consume(self.on_response, no_ack=True)

    async def on_response(self, message: AbstractIncomingMessage) -> Awaitable[None]:
        """Handles response"""
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self._futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, queue_name: str, callback_queue_name: str, message_body: dict) -> Awaitable[asyncio.Future]:
        """Sends message to RPC server"""
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self._futures[correlation_id] = future

        await self._channel.default_exchange.publish(
            Message(
                body=json.dumps(message_body).encode("utf-8"),
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=callback_queue_name,
            ),
            routing_key=queue_name,
            timeout=100
        )

        return await future
