from modules.rabbitmq.rpc.server import RPCServer


class GatewayRPCServer(RPCServer):
    """RabbitMQ RPC server"""

    _PUBLISH_EXCHANGE_NAME: str = 'gateway_exchange'

    QUEUE_NAME_TO_HANDLER: dict = {
        'gateway_request_queue': 'handle_request',
    }

    async def handle_request(self, message_body: dict):
        """Request handling"""
        return {"text": f"pong from gateway, recieved: '{message_body}'"}
