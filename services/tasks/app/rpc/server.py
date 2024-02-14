from modules.rpc.server import RPCServer


class TasksRPCServer(RPCServer):
    """RabbitMQ RPC server"""

    QUEUE_NAME_TO_HANDLER: dict = {
        'tasks.create': 'create_tasks',
        'tasks.read': 'read_tasks',
        'task.done': 'complete_task',
        'task.delete': 'delete_task',
        'task.update': 'update_task',
        'tasks.ping': 'ping'
    }

    async def create_tasks(self, message_body: dict):
        raise NotImplementedError
    
    async def read_tasks(self, message_body: dict):
        raise NotImplementedError
    
    async def complete_task(self, message_body: dict):
        raise NotImplementedError
    
    async def delete_task(self, message_body: dict):
        raise NotImplementedError 
   
    async def update_task(self, message_body: dict):
        raise NotImplementedError
    
    async def ping(self, message_body: dict):
        return {"text": "pong from tasks"}