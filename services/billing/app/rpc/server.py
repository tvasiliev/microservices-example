from modules.rabbitmq.rpc.server import RPCServer


class BillingRPCServer(RPCServer):
    """RabbitMQ RPC server"""

    QUEUE_NAME_TO_HANDLER: dict = {
        'billing.create': 'create_wallet',
        'billing.read': 'read_wallet',
        'billing.replenish': 'replenish_wallet',
        'billing.withdraw': 'withdraw_from_wallet',
        'billing.freeze': 'freeze_wallet_balance',
        'billing.ping': 'ping'
    }

    async def create_wallet(self, message_body: dict):
        raise NotImplementedError
    
    async def read_wallet(self, message_body: dict):
        raise NotImplementedError
    
    async def replenish_wallet(self, message_body: dict):
        raise NotImplementedError
    
    async def withdraw_from_wallet(self, message_body: dict):
        raise NotImplementedError 
   
    async def freeze_wallet_balance(self, message_body: dict):
        raise NotImplementedError
    
    async def ping(self, message_body: dict):
        return {"text": "pong from billing"}