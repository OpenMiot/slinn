from . import WebSocketGroup
import functools


class AsyncWebSocketGroup(WebSocketGroup):
    def __getattr__(self, key):
        @functools.wraps(self.__do)
        async def wrapped(*args, **kwargs):
            return await self.__do(key, *args, **kwargs)
        return wrapped
    
    async def __do(self, name, *args, **kwargs):
        if name not in ('read', '_send', 'send_binary', 'send_text', 'ping', 'pong', 'close', 'send'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        exclude = kwargs.pop('exclude', [])
        for i, connection in enumerate(self.connections):
            if connection.closed:
                del self.connections[i]
                continue
            if connection in exclude:
                continue
            await getattr(connection, name)(*args, **kwargs)
        for subgroup in self.subgroups:
            await getattr(subgroup, name)(*args, **kwargs)