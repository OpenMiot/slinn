from . import HttpResponseHeader, HttpResponseChunk, Request
from .utils import representate
import gzip


class HttpResponse(HttpResponseHeader, HttpResponseChunk):
    """
    Base class for all HTTP responses
    """

    def __init__(self, payload: any, data: list[tuple] = None, status: str = '200 OK',
                 content_type: str = 'text/plain; charset=utf-8', use_gzip=True,
                 request: Request = None) -> None:
        payload = representate(payload)
        use_gzip = use_gzip and request and 'gzip' in request.encoding
        if use_gzip:
            payload = gzip.compress(payload)

        HttpResponseHeader.__init__(self, (data if data else []) + [
            ('Content-Length', len(payload))
        ], status, content_type, use_gzip)
        HttpResponseChunk.__init__(self, payload)
