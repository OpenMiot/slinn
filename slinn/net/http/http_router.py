from typing import Callable
from slinn.net.http.responses.http_response_chunk import HttpResponseChunk
from slinn.net.http.filters import Filter
from slinn.net.http import HttpRequest
from slinn.net.tcp import TcpRouterProtocol
from slinn.net.http.filters import Path
from slinn.net import Endpoint
from slinn import utils
import functools


class HttpRouter(TcpRouterProtocol):
    def __init__(self, *hosts, prefix: str = ''):
        self.endpoints = []
        self.hosts = hosts if hosts else ('.*',)
        self.prefix = prefix

        self.get = functools.partial(self._register_handler_decorator, methods=('GET', ))
        self.post = functools.partial(self._register_handler_decorator, methods=('POST',))
        self.patch = functools.partial(self._register_handler_decorator, methods=('PATCH',))
        self.put = functools.partial(self._register_handler_decorator, methods=('PUT',))
        self.delete = functools.partial(self._register_handler_decorator, methods=('DELETE',))
        self.options = functools.partial(self._register_handler_decorator, methods=('OPTIONS',))

    def __call__(self, request_filter: Filter) -> Callable[[Callable], Callable]:
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            self.endpoints.append(Endpoint(request_filter, wrapper, request_filter.args))
            return wrapper

        return decorator

    def check(self, request: HttpRequest) -> bool:
        return len(self.hosts) == 0 or True in [utils.restartswith(request.host, _host) for _host in self.hosts]

    def _register_handler_decorator(self, path: str = '', methods: tuple[str, ...] = ()):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            _path = Path(self.prefix + ('' if path.startswith('/') else ('/' if path else '/?')) + path, methods)
            self.endpoints.append(Endpoint(_path, func, _path.args))
            return wrapper

        return decorator

    def static(self, link: str, response_class: type[HttpResponseChunk], *args, **kwargs) -> HttpRouter:
        async def handler():
            return response_class(*args, **kwargs)

        _path = Path(self.prefix + link)
        self.endpoints.append(Endpoint(_path, handler, _path.args))
        return self