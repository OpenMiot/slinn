import functools


class WebSocketGroup:
    def __init__(self):
        self.connections = []
        self.subgroups = []

    def __getattr__(self, key):
        @functools.wraps(self.__do)
        def wrapped(*args, **kwargs):
            return self.__do(key, *args, **kwargs)
        return wrapped
    
    def add(self, connection):
        self.connections.append(connection)
    
    def __do(self, name, *args, **kwargs):
        if name not in ('read', '_send', 'send_binary', 'send_text', 'ping', 'pong', 'close', 'send'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        for i, connection in enumerate(self.connections):
            if connection.closed:
                del self.connections[i]
                continue
            if 'exclude' in kwargs.keys() and connection in kwargs['exclude']:
                continue
            return getattr(connection, name)(*args, **kwargs)
        for subgroup in self.subgroups:
            getattr(subgroup, name)(*args, **kwargs)
