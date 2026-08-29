from slinn.net.http.responses import HttpResponse, HttpBodyMixin
from slinn.net.http import HttpHandlerProcessor
from slinn import MiddlewareProtocol
import zlib


class GzipMiddleware(MiddlewareProtocol):
    def __init__(self):
        ...
    
    def __call__(self, func):
        def compress_response(compressor, response: HttpResponse) -> HttpResponse:
            response.headers.add('Content-Encoding', 'gzip')
            async def gzip_hook(self, **kwargs):
                self.payload = compressor.compress(self.payload)
                return kwargs
            response.hooks[gzip_hook] = (HttpBodyMixin, )
            return response
        
        async def wrapper(request, http_codes_router, **kwargs):
            compressor = zlib.compressobj(wbits = 31)
            async for chunk in HttpHandlerProcessor.process(
                func, request = request, http_codes_router = http_codes_router, **kwargs
            ):
                yield compress_response(compressor, chunk)
            yield compressor.flush()
        return wrapper
