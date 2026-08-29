from slinn.net.http import HttpHandlerProcessor
lazy from slinn.net.http import HttpRouter
from slinn import MiddlewareProtocol
from collections.abc import Callable


class CorsMiddleware(MiddlewareProtocol):
    def __init__(self, router: HttpRouter):
        self.router = router
    
    def __call__(self, func: Callable) -> Callable:
        async def wrapper(recv_headers, **kwargs):
            rule = None
            for _path, _rule in self.router.preflights.items():
                if _path.check(recv_headers) and _rule.matches(recv_headers):
                    rule = _rule
                    break
            
            async for chunk in HttpHandlerProcessor.process(
                func, recv_headers = recv_headers, **kwargs
            ):
                if rule:
                    chunk.headers.extend(rule.get_headers(recv_headers.get('Origin')))
                yield chunk
        return wrapper