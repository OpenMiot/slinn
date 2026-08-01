from .http_response import HttpResponse
from typing import Any
import json


class HttpJSONResponse(HttpResponse):
    """
    HttpResponse-based class, that uses keyword arguments to response JSON object
    """
    def __init__(
        self,
        **payload: Any
    ):
        self.data = payload['__data'] if '__data' in payload.keys() else None
        self.status = payload['__status'] if '__status' in payload.keys() else '200 OK'
        self.content_type = payload['__content_type'] if '__content_type' in payload.keys() else 'text/plain; charset=utf-8'
        payload.pop('__data', None)
        payload.pop('__status', None)
        payload.pop('__content_type', None)
        super().__init__(payload=json.dumps(payload, ensure_ascii=False), data=self.data, status=self.status, content_type=self.content_type)
