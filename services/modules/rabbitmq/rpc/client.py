
import asyncio
import json
import uuid
from typing import MutableMapping, Awaitable

from aio_pika import Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.exceptions import DeliveryError
from modules.rabbitmq.client import RabbitMQClient


class RPCClient(RabbitMQClient):
    """Client for RPC RabbitMQ calls"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._futures: MutableMapping[str, asyncio.Future] = {}

    async def _on_response(self, message: AbstractIncomingMessage) -> Awaitable[None]:
        """Handles response"""
        async with message.process(ignore_processed=True):
            if message.correlation_id is None:
                self._logger.warn("Bad message %r", message)
                await message.reject()
                return

            future: asyncio.Future = self._futures.pop(message.correlation_id, None)
            if future:
                await message.ack()
            else:
                await message.reject()

        future.set_result(message.body)


    async def request(self, queue_name: str, callback_queue_name: str, message_body: dict) -> Awaitable[asyncio.Future]:
        """Sends request to RPC server"""
        callback_queue = await self._input_channel.declare_queue(name=callback_queue_name, exclusive=True)
        await callback_queue.consume(self._on_response, no_ack=False)

        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self._futures[correlation_id] = future
        
        self._logger.info('Sending request to queue "%s", waiting response from queue "%s"', queue_name, callback_queue_name)

        await self.publish(
            message=Message(
                body=json.dumps(message_body).encode("utf-8"),
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=callback_queue_name,
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
            timeout=5,
            mandatory=True
        )

        return await future

    async def _handle_delivery_error(self, exception: DeliveryError) -> Awaitable[None]:
        super()._handle_delivery_error(exception)
        self._futures.pop(exception.message.correlation_id, None)
