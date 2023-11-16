import asyncio

from modules.rpc.server import RPCServer

from .config import config


class TasksRPCServer(RPCServer):
    """RPC server for tasks microservice"""

    async def handle_message(self, message_body: dict):
        """Handles message body"""
        return {"text": "pong"}


if __name__ == "__main__":
    server = TasksRPCServer(
        queue_name=config.QUEUE_NAME,
        broker_url=config.RABBITMQ_URL
    )

    asyncio.run(server.listen())