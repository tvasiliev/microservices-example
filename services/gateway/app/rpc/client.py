from modules.rabbitmq.rpc.client import RPCClient


class GatewayRPCClient(RPCClient):
    """RabbitMQ RPC client"""

    _CALLBACK_QUEUE_NAME: str = 'gateway_callback_queue'
    _CALLBACK_ROUTING_KEY: str = 'gateway.callback'
    _PUBLISH_EXCHANGE_NAME: str = 'gateway_exchange'
 