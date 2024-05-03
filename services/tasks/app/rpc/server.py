from modules.rabbitmq.rpc.server import RPCServer


class TasksRPCServer(RPCServer):
    """RabbitMQ RPC server"""

    _PUBLISH_EXCHANGE_NAME: str = 'tasks_exchange'

    QUEUE_NAME_TO_HANDLER: dict = {
        'tasks_request_queue': 'handle_request',
    }

    async def handle_request(self, message_body: dict):
        """Request handling"""
        return {"text": f"pong from tasks, recieved: '{message_body}'"}
