import asyncio
from typing import Awaitable

from aio_pika import connect
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractExchange
from aio_pika.exceptions import DeliveryError
from modules.log import get_logger


async def create_connection(broker_url: str) -> AbstractConnection:
    """Creates connection to RabbitMQ broker"""
    return await connect(url=broker_url)


class RabbitMQClient:
    """Base broker interface (separated I/O due to flow control)
    Connections must be created outside of this class and should
    be passed in every instance so there is constant amount of connections (2) per process
    """

    _input_channel: AbstractChannel
    _output_channel: AbstractChannel
    _exchange: AbstractExchange
    _PUBLISH_EXCHANGE_NAME: str = NotImplemented

    def __init__(
        self, input_connection: AbstractConnection,
        output_connection: AbstractConnection, publish_retries: int
    ) -> None:
        self._input_connection = input_connection
        self._output_connection = output_connection
        self._publish_retries = publish_retries
        self._logger = get_logger()

    async def open_channels(self) -> Awaitable[None]:
        """Opens channels from RabbitMQ connections"""
        self._input_channel = await self._input_connection.channel()
        await self._input_channel.set_qos(prefetch_count=500)

        self._output_channel = await self._output_connection.channel(publisher_confirms=True, on_return_raises=True)
        self._exchange = await self._output_channel.get_exchange(self._PUBLISH_EXCHANGE_NAME)

    async def close_channels(self) -> Awaitable[None]:
        """Closes channels from RabbitMQ connections"""
        await self._input_channel.close()
        await self._output_channel.close()
    
    async def publish(self, **kwargs) -> Awaitable[None]:
        """Publishes message and retries on DeliveryError"""
        retries = self._publish_retries
        while True:
            try:
                await self._exchange.publish(**kwargs)
                return
            except DeliveryError as exc:
                retries -= 1
                if not retries:
                    await self._handle_delivery_error(exc)
    
    async def consume(self, queue_name: str, **kwargs) -> Awaitable[None]:
        """Consumes messages from given queue"""
        queue = await self._input_channel.get_queue(name=queue_name)
        await queue.consume(**kwargs)

    async def _handle_delivery_error(self, exception: DeliveryError) -> None:
        self._logger.warn(exception)
