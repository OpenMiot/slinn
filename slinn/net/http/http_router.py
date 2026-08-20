from slinn.net.http.responses import HttpBodyMixin, HttpResponse
from slinn.net.http.filters import Filter
from slinn.net.http import HttpRequest
from slinn.net.http.filters import Path
from slinn.net import Endpoint
from slinn import MiddlewareProtocol, utils
from collections.abc import Callable
import functools
import inspect


class HttpRouter:
    def __init__(self, *hosts, prefix: str = ''):
        self.endpoints = []
        self.middlewares = []
        self.hosts = hosts if hosts else ('.*',)
        self.prefix = prefix

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
    
    def get_endpoint(self, request: HttpRequest, **kwargs) -> Endpoint | None:
        for endpoint in self.endpoints:
            if endpoint.filter.check(request):
                return endpoint.apply_decorators(self.middlewares)

    def check(self, request: HttpRequest, **kwargs) -> bool:
        return not len(self.hosts) or True in [
            utils.restartswith(request.headers.authority, _host) for _host in self.hosts
        ]

    def _register_handler_decorator(self, path: str = '', methods: tuple[str, ...] = ()):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            _path = Path(self.prefix + ('' if path.startswith('/') else ('/' if path else '/?')) + path, methods)
            self.endpoints.append(Endpoint(_path, func, _path.args))
            return wrapper
        return decorator

    def static(self, link: str, response_class: type[HttpBodyMixin], *args, **kwargs) -> HttpRouter:
        @functools.cache
        async def handler():
            return response_class(*args, **kwargs)

        _path = Path(self.prefix + link)
        self.endpoints.append(Endpoint(_path, handler, _path.args))
        return self

    def get(self, path: str = '', head: bool = True):
        def decorator(func):
            _get_path = Path(self.prefix + ('' if path.startswith('/') else ('/' if path else '/?')) + path, ('GET', ))
            self.endpoints.append(Endpoint(_get_path, func, _get_path.args))
            
            if head:
                if inspect.isasyncgenfunction(func):
                    @functools.wraps(func)
                    async def head_wrapper(*args, **kwargs):
                        async for chunk in func(*args, **kwargs):
                            if isinstance(chunk, HttpResponse):
                                chunk.excluded_mixins.append(HttpBodyMixin)
                            yield chunk
                else:
                    @functools.wraps(func)
                    async def head_wrapper(*args, **kwargs):
                        return await func(*args, **kwargs)
                
                head_wrapper.ignore_body = True
                _head_path = Path(self.prefix + ('' if path.startswith('/') else ('/' if path else '/?')) + path, ('HEAD', ))
                self.endpoints.append(Endpoint(_head_path, head_wrapper, _head_path.args))
            
            return func
        return decorator

    def register_middleware(self, middleware: MiddlewareProtocol):
        self.middlewares.append(middleware)
