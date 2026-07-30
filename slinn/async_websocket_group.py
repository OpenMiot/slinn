from . import WebSocketGroup, WebSocketFrame
from typing import Callable, Any, Awaitable
import functools


class AsyncWebSocketGroup(WebSocketGroup):
    def __getattr__(self, key: str) -> Callable[..., Awaitable[list[WebSocketFrame]]]:
        @functools.wraps(self.__do)
        async def wrapped(*args, **kwargs):
            return await self.__do(key, *args, **kwargs)
        return wrapped
    
    async def __do(self, name, *args, **kwargs) -> list[WebSocketFrame]:
        if name not in ('read', '_send', 'send_binary', 'send_text', 'ping', 'pong', 'close', 'send'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        results = []
        exclude = kwargs.pop('exclude', ())

        for i, connection in enumerate(self.connections):
            if connection.closed:
                del self.connections[i]
                continue
            if connection in exclude:
                continue
            result = await getattr(connection, name)(*args, **kwargs)
            if name == 'read':
                results.append(result)
        for subgroup in self.subgroups:
            results_subgroup = await getattr(subgroup, name)(*args, **kwargs)
            if name == 'read':
                results.extend(results_subgroup)

        return results
