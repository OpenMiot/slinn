from __future__ import annotations
from typing import Any, Optional
from .http_response import HttpResponse
from .request import Request


class HttpAPIResponse(HttpResponse):
    
    """
    Like HttpResponse, but with header `Access-Control-Allow-Origin: *`
    """

    def __init__(
            self,
            payload: Any,
            data: list[tuple] = None,
            status: str = '200 OK',
            content_type: str = 'text/plain; charset=utf-8',
            use_gzip: bool = True,
            request: Optional[Request] = None):
        super().__init__(payload, data, status, content_type, use_gzip, request)
        self.data.append(('Access-Control-Allow-Origin', '*'))
