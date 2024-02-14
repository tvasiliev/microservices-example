from modules.rpc.server import RPCServer


class GatewayRPCServer(RPCServer):
    """RabbitMQ RPC server"""

    QUEUE_NAME_TO_HANDLER: dict = {
        'gateway.ping': 'ping',
    }

    async def ping(self, message_body: dict):
        return {"text": "pong from gateway"}
