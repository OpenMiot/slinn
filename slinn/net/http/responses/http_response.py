from . import HttpHeaderResponse, HttpChunkResponse
from slinn.net.http import HttpHeaders
from slinn.utils import representate
from typing import Any, Optional
import gzip


class HttpResponse(HttpHeaderResponse, HttpChunkResponse):
    """
    Base class for all HTTP responses
    """

    def __init__(
        self,
        payload: Any,
        data: Optional[HttpHeaders] = None,
        status: str = '200 OK',
        content_type: str = 'text/plain; charset=utf-8',
        use_gzip: bool = True,
        headers: HttpHeaders | None = None
    ):
        payload = representate(payload)
        #use_gzip = use_gzip and request and 'gzip' in request.accept_encoding
        use_gzip = False
        if use_gzip:
            payload = gzip.compress(payload)

        HttpHeaderResponse.__init__(
            self,
            (data or HttpHeaders()).add('Content-Length', len(payload)),
            status,
            content_type
        )
        HttpChunkResponse.__init__(self, payload)

    def make(self, headers: HttpHeaders) -> bytes:
        return HttpChunkResponse.make(self, headers)
