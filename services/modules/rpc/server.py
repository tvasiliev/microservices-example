import asyncio
import json
from typing import Awaitable

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, AbstractConnection, AbstractChannel
from modules.app.config import get_logger


class RPCServer:
    """RPC server that handles messages from given queue"""

    QUEUE_NAME_TO_HANDLER: dict = NotImplemented

    _channel: AbstractChannel

    def __init__(self, connection: AbstractConnection) -> None:
        self._connection = connection
        self._logger = get_logger()

    async def create_channel(self) -> Awaitable[None]:
        self._channel = await self._connection.channel()

    async def close_channel(self) -> Awaitable[None]:
        await self._channel.close()

    async def _listen(self, queue_name: str) -> Awaitable[None]:
        if queue_name not in self.QUEUE_NAME_TO_HANDLER:
            raise ValueError(
                f'Cannot listen to queue "{queue_name}": '
                'all queues and their handlers should be declared in class {self.__classname__}'
            )

        queue = await self._channel.declare_queue(queue_name)

        self._logger.info("Awaiting RPC requests from queue %s", queue_name)

        async with queue.iterator() as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                async with message.process(requeue=False):
                    assert message.reply_to is not None

                    message_body = json.loads(message.body.decode())
                    self._logger.info("Recieved request (%s): %s", message.message_id, message_body)
                    response = await getattr(self, self.QUEUE_NAME_TO_HANDLER[queue_name])(message_body)

                    await self._channel.default_exchange.publish(
                        Message(
                            body=json.dumps(response).encode("utf-8"),
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                        timeout=5
                    )
                    self._logger.info("Request %s complete", message.message_id)

    async def listen(self) -> Awaitable[None]:
        """Listens on all defined queues infinitely"""
        await asyncio.gather(*(self._listen(queue_name) for queue_name in self.QUEUE_NAME_TO_HANDLER))
