import asyncio
import json
import os
from typing import Awaitable

from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage


class RPCServer:
    """RPC server that handles messages from given queue"""

    QUEUE_NAME_TO_HANDLER: dict = NotImplemented

    def __init__(self, broker_url: str) -> None:
        self._broker_url = broker_url

    async def _listen(self, queue_name: str) -> Awaitable[None]:
        if queue_name not in self.QUEUE_NAME_TO_HANDLER:
            raise ValueError(
                f'Cannot listen to queue "{queue_name}": '
                'all queues and their handlers should be declared in class {self.__classname__}'
            )

        connection = await connect(self._broker_url)
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name)

        print(f"Awaiting RPC requests from queue {queue_name}")

        async with queue.iterator() as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                async with message.process(requeue=False):
                    assert message.reply_to is not None

                    message_body = json.loads(message.body.decode())
                    print(f"Recieved request ({message.message_id}): {message_body}")
                    response = await getattr(self, self.QUEUE_NAME_TO_HANDLER[queue_name])(message_body)

                    await channel.default_exchange.publish(
                        Message(
                            body=json.dumps(response).encode("utf-8"),
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                        timeout=100
                    )
                    print(f"Request {message.message_id} complete")

    async def listen(self) -> Awaitable[None]:
        """Listens on all defined queues infinitely"""
        await asyncio.gather(*(self._listen(queue_name) for queue_name in self.QUEUE_NAME_TO_HANDLER))
