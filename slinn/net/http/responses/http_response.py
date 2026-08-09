from . import HttpResponseHeader, HttpResponseChunk
from slinn.net.http import HttpRequest
from slinn.utils import representate
from typing import Any, Optional
import gzip


class HttpResponse(HttpResponseHeader, HttpResponseChunk):
    """
    Base class for all HTTP responses
    """

    def __init__(
        self,
        payload: Any,
        data: Optional[list[tuple]] = None,
        status: str = '200 OK',
        content_type: str = 'text/plain; charset=utf-8',
        use_gzip: bool = True,
        request: Optional[HttpRequest] = None
    ):
        payload = representate(payload)
        use_gzip = use_gzip and request and 'gzip' in request.accept_encoding
        if use_gzip:
            payload = gzip.compress(payload)

        HttpResponseHeader.__init__(self, (data if data else []) + [
            ('Content-Length', len(payload))
        ], status, content_type, use_gzip)
        HttpResponseChunk.__init__(self, payload)

    def make(self, request: HttpRequest) -> bytes:
        return HttpResponseHeader.make(self, request) + HttpResponseChunk.make(self, request)
