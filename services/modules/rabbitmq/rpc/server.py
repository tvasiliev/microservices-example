import asyncio
import json
from typing import Awaitable

from aio_pika import Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage
from modules.rabbitmq.client import RabbitMQClient


class RPCServer(RabbitMQClient):
    """RPC server that handles messages from given queue"""

    QUEUE_NAME_TO_HANDLER: dict = NotImplemented

    async def _listen(self, queue_name: str) -> Awaitable[None]:
        if queue_name not in self.QUEUE_NAME_TO_HANDLER:
            raise ValueError(
                f'Cannot listen to queue "{queue_name}": '
                'all queues and their handlers should be declared in class {self.__classname__}'
            )

        queue = await self._input_channel.get_queue(queue_name)

        self._logger.info("Awaiting RPC requests from queue %s", queue_name)

        async with queue.iterator(no_ack=False) as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                async with message.process(ignore_processed=True):
                    message_body = json.loads(message.body.decode())
                    await message.ack()

                    handler_result = await getattr(self, self.QUEUE_NAME_TO_HANDLER[queue_name])(message_body)

                    if message.reply_to is not None:
                        # recieved request, sending response
                        self._logger.info(
                            "Recieved request (%s): %s [correlation_id: %s]",
                            message.message_id, message_body, message.correlation_id
                        )

                        await self.publish(
                            message=Message(
                                body=json.dumps(handler_result).encode("utf-8"),
                                correlation_id=message.correlation_id,
                                delivery_mode=DeliveryMode.PERSISTENT
                            ),
                            routing_key=message.reply_to,
                            timeout=5,
                            mandatory=True
                        )

    async def listen(self) -> Awaitable[None]:
        """Listens on all defined queues infinitely"""
        await asyncio.gather(*(self._listen(queue_name) for queue_name in self.QUEUE_NAME_TO_HANDLER))
