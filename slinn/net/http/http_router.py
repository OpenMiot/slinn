from slinn.net.http.responses import HttpBodyMixin, HttpResponse
from slinn.net.http.filters import Filter, Path
from slinn.net.http.middlewares import CorsMiddleware
from slinn.net.http import HttpHeaders
from slinn.net import Endpoint
from slinn.utils import optional, restartswith
from slinn import MiddlewareProtocol
from collections.abc import Callable
from typing import Any
import functools
import inspect
import re


class HttpRouter:
    class PreflightRule:
        def __init__(self, origin_pattern: str, methods: list[str], headers: list[str], max_age: int):
            self.origin = re.compile(origin_pattern)
            self.methods = methods
            self.headers = {header.title() for header in headers}
            self.max_age = max_age
            
        def matches(self, recv_headers: HttpHeaders):
            return self.origin.match(recv_headers.get('Origin'))
        
        def is_allowed(self, recv_headers: HttpHeaders):
            return (
                self.matches(recv_headers) and 
                recv_headers.get('Access-Control-Request-Method') in self.methods and 
                {
                    header.strip().title()
                    for header in recv_headers.get('Access-Control-Request-Headers', '').split(',')
                }.issubset(self.headers | {''})
            )
        
        def get_headers(self, origin: str):
            return HttpHeaders(default_headers={
                'Access-Control-Allow-Origin': (origin,),
                'Access-Control-Allow-Methods': (', '.join(self.methods),),
                'Access-Control-Allow-Headers': (', '.join(self.headers),),
                'Access-Control-Max-Age': (str(self.max_age),)
            })
        
        
    def __init__(self, *hosts: str, prefix: str = ''):
        self.endpoints: list[Endpoint] = []
        self.middlewares: list[MiddlewareProtocol] = []
        self.hosts: tuple[str, ...] = hosts if hosts else ('.*',)
        self.prefix: str = prefix
        self.preflights: dict[Path, HttpRouter.PreflightRule] = {}

        self.post = functools.partial(self._register_handler_decorator, methods = ('POST',))
        self.patch = functools.partial(self._register_handler_decorator, methods = ('PATCH',))
        self.put = functools.partial(self._register_handler_decorator, methods = ('PUT',))
        self.delete = functools.partial(self._register_handler_decorator, methods = ('DELETE',))
        self.head = functools.partial(self._register_handler_decorator, methods = ('HEAD',))
        self.connect = functools.partial(self._register_handler_decorator, methods = ('CONNECT',))
        self.trace = functools.partial(self._register_handler_decorator, methods = ('TRACE',))
        
        self.register_middleware(CorsMiddleware(self))

    def __call__(self, request_filter: Filter) -> Callable[[Callable], Callable]:
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            self.endpoints.append(Endpoint(request_filter, wrapper, request_filter.args))
            return wrapper
        return decorator
    
    def get_endpoint(self, recv_headers: HttpHeaders, **kwargs) -> Endpoint | None:
        for endpoint in self.endpoints:
            if endpoint.filter.check(recv_headers):
                return endpoint.apply_decorators(self.middlewares)

    def check(self, recv_headers: HttpHeaders, **kwargs) -> bool:
        return not len(self.hosts) or (True in [
            restartswith(recv_headers.authority, _host) for _host in self.hosts
        ])

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
                _head_path = Path(
                    self.prefix + ('' if path.startswith('/') else ('/' if path else '/?')) + path, ('HEAD', )
                )
                self.endpoints.append(Endpoint(_head_path, head_wrapper, _head_path.args))
            
            return func
        return decorator

    def options(self, path: str = ''):
        def decorator(func):
            _path = Path(self.prefix + ('' if path.startswith('/') else ('/' if path else '/?')) + path, ('OPTIONS', ))
            
            def is_cors_preflight(recv_headers: HttpHeaders, **kwargs) -> bool:
                return (
                    'Access-Control-Request-Method' in recv_headers and
                    _path.check(recv_headers = recv_headers, **kwargs) and 
                    'Origin' in recv_headers
                )
            
            def make_cors_preflight_response(recv_headers: HttpHeaders) -> Any:
                for preflight_path in self.preflights:
                    if preflight_path.check(recv_headers, skip_methods_check = True):
                        preflight_rule = self.preflights[preflight_path]
                        if preflight_rule.is_allowed(recv_headers):
                            return HttpResponse(
                                status = '204 No Content',
                                headers = preflight_rule.get_headers(recv_headers.get('Origin'))
                            )
                return 204
            
            async def wrapper(recv_headers: HttpHeaders, **kwargs):
                coro = optional(func, recv_headers = recv_headers, **kwargs)
                if is_cors_preflight(recv_headers = recv_headers, **kwargs):
                    if inspect.isasyncgenfunction(func):
                        async for chunk in coro:
                            yield make_cors_preflight_response(recv_headers = recv_headers)
                            return
                    else:
                        yield make_cors_preflight_response(recv_headers = recv_headers)
                if inspect.isasyncgenfunction(func):
                    async for chunk in coro:
                        yield chunk
                else:
                    yield await coro
        
            self.endpoints.append(Endpoint(_path, wrapper, _path.args))
        return decorator

    def preflight(
        self,
        path: str,
        origin_pattern: str,
        methods: list[str] | None = None,
        headers: list[str] | None = None,
        max_age: int = 86400
    ):
        self.preflights[Path(path, tuple(set(methods)))] = HttpRouter.PreflightRule(
            origin_pattern = origin_pattern,
            methods = methods or [],
            headers = headers or [],
            max_age = max_age
        )
        @self.options(path)
        async def empty_handler():
            return 400

    def register_middleware(self, middleware: MiddlewareProtocol):
        self.middlewares.append(middleware)
