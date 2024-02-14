from aio_pika import connect
from aio_pika.abc import AbstractConnection


async def create_connection(broker_url: str) -> AbstractConnection:
    """Creates connection to RabbitMQ broker"""
    return await connect(url=broker_url)
