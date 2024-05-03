from modules.rabbitmq.rpc.client import RPCClient


class TasksRPCClient(RPCClient):
    """RabbitMQ RPC client"""

    _CALLBACK_QUEUE_NAME: str = 'tasks_callback_queue'
    _CALLBACK_ROUTING_KEY: str = 'tasks.callback'
    _PUBLISH_EXCHANGE_NAME: str = 'tasks_exchange'
 