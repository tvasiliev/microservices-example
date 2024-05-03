from modules.rabbitmq.rpc.client import RPCClient


class BillingRPCClient(RPCClient):
    """RabbitMQ RPC client"""

    _CALLBACK_QUEUE_NAME: str = 'billing_callback_queue'
    _CALLBACK_ROUTING_KEY: str = 'billing.callback'
    _PUBLISH_EXCHANGE_NAME: str = 'billing_exchange'
 