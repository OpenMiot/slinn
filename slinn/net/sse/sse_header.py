from slinn import HttpResponseHeader
from typing import Optional


class SSEHeader(HttpResponseHeader):
    def __init__(self, cors: Optional[str] = None):
        super().__init__(
            data=[
                ('Cache-Control', 'no-cache'),
                ('Connection', 'keep-alive')
            ] + ([('Access-Control-Allow-Origin', cors)] if cors else []),
            content_type='text/event-stream; charset=utf-8',
            use_gzip=False
        )
