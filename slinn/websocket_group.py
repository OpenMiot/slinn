from __future__ import annotations
import functools
from typing import Callable, Any
from . import WebSocketFrame, WebSocketConnection


class WebSocketGroup:
    def __init__(self):
        self.connections = []
        self.subgroups = []

    def __getattr__(self, key: str) -> Callable[..., list[WebSocketFrame]]:
        @functools.wraps(self.__do)
        def wrapped(*args, **kwargs):
            return self.__do(key, *args, **kwargs)
        return wrapped
    
    def add(self, connection: WebSocketConnection):
        self.connections.append(connection)

    def add_subgroup(self, subgroup: WebSocketGroup):
        self.subgroups.append(subgroup)
    
    def __do(self, name, *args, **kwargs) -> list[WebSocketFrame]:
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
            result = getattr(connection, name)(*args, **kwargs)
            if name == 'read':
                results.append(result)
        for subgroup in self.subgroups:
            results_subgroup = getattr(subgroup, name)(*args, **kwargs)
            if name == 'read':
                results.extend(results_subgroup)

        return results
