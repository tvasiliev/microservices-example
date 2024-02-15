
import asyncio
import json
import uuid
from typing import MutableMapping, Awaitable

from aio_pika import Message
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)
from modules.log import get_logger


class RPCClient:
    """Client for RPC RabbitMQ calls"""

    _channel: AbstractChannel
    _callback_queue: AbstractQueue

    def __init__(self, connection: AbstractConnection) -> None:
        self._connection = connection
        self._futures: MutableMapping[str, asyncio.Future] = {}
        self._logger = get_logger()

    async def create_channel(self) -> Awaitable[None]:
        self._channel = await self._connection.channel()

    async def close_channel(self) -> Awaitable[None]:
        await self._channel.close()

    async def consume(self, queue_name: str) -> Awaitable[None]:
        """Consumes certain queue"""
        queue = await self._channel.declare_queue(name=queue_name, exclusive=True)
        await queue.consume(self.on_response, no_ack=True)

    async def on_response(self, message: AbstractIncomingMessage) -> Awaitable[None]:
        """Handles response"""
        if message.correlation_id is None:
            self._logger.warn("Bad message %r", message)
            return

        future: asyncio.Future = self._futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, queue_name: str, callback_queue_name: str, message_body: dict) -> Awaitable[asyncio.Future]:
        """Sends message to RPC server"""
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self._futures[correlation_id] = future
        
        self._logger.info('Sending request to queue "%s", waiting response from queue "%s"', queue_name, callback_queue_name)
        await self._channel.default_exchange.publish(
            Message(
                body=json.dumps(message_body).encode("utf-8"),
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=callback_queue_name,
            ),
            routing_key=queue_name,
            timeout=5
        )

        return await future
