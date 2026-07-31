"""Import slinn`s modules"""
from . import Path, Endpoint, Filter, TCPResponseChunk, utils
from typing import Callable
import functools


class Router:

    """
    Class for handling requests
    """

    def __init__(self, *hosts, prefix: str = ''):
        self.handles = []
        self.hosts = hosts if hosts else ('.*',)
        self.prefix = prefix

        self.get = functools.partial(self._register_handler_decorator, methods=('GET', ))
        self.post = functools.partial(self._register_handler_decorator, methods=('POST',))
        self.patch = functools.partial(self._register_handler_decorator, methods=('PATCH',))
        self.put = functools.partial(self._register_handler_decorator, methods=('PUT',))
        self.delete = functools.partial(self._register_handler_decorator, methods=('DELETE',))
        self.options = functools.partial(self._register_handler_decorator, methods=('OPTIONS',))

    def __call__(self, _filter: Filter) -> Callable[[Callable], Callable]:
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            self.handles.append(Endpoint(_filter, wrapper, _filter.args))
            return wrapper

        return decorator

    def check(self, host: str) -> bool:
        return len(self.hosts) == 0 or True in [utils.restartswith(host, _host) for _host in self.hosts]

    def _register_handler_decorator(self, path: str = '', methods: tuple[str, ...] = ()):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            
            _path = Path(self.prefix + ('' if path.startswith('/') else ('/' if path else '/?')) + path, methods)
            self.handles.append(Endpoint(_path, func, _path.args))
            return wrapper

        return decorator

    def static(self, link: str, response_class: type[TCPResponseChunk], *args, **kwargs) -> Router:
        async def handler():
            return response_class(*args, **kwargs)

        _path = Path(self.prefix + link)
        self.handles.append(Endpoint(_path, handler, _path.args))
        return self
