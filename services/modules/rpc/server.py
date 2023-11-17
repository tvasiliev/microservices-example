import asyncio
import json
import os

from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage


class RPCServer:
    """RPC server that handles messages from given queue"""

    def __init__(self, broker_url: str) -> None:
        self.broker_url = broker_url

    async def handle_message(self, message_body: dict) -> any:
        """Handles message body"""
        raise NotImplementedError

    async def listen(self, queue_name: str) -> None:
        """Listens on queue infinitely"""
        connection = await connect(os.environ.get('RMQ_URL'))
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name)

        print("Awaiting RPC requests")

        async with queue.iterator() as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                async with message.process(requeue=False):
                    assert message.reply_to is not None

                    message_body = json.loads(message.body.decode())
                    print(f"Recieved request ({message.message_id}): {message_body}")

                    response = await self.handle_message(message_body)

                    await channel.default_exchange.publish(
                        Message(
                            body=json.dumps(response).encode("utf-8"),
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                        timeout=100
                    )
                    print(f"Request {message.message_id} complete")
