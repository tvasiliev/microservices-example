from modules.rabbitmq.rpc.server import RPCServer


class BillingRPCServer(RPCServer):
    """RabbitMQ RPC server"""

    _PUBLISH_EXCHANGE_NAME: str = 'billing_exchange'

    QUEUE_NAME_TO_HANDLER: dict = {
        'billing_request_queue': 'handle_request',
    }

    async def handle_request(self, message_body: dict):
        """Request handling"""
        return {"text": f"pong from billing, recieved: '{message_body}'"}
