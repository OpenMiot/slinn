from . import HttpResponseHeader


class SSEHeader(HttpResponseHeader):
    def __init__(self, cors):
        super().__init__(
            data=[
                ('Cache-Control', 'no-cache'),
                ('Connection', 'keep-alive'),
                ('Access-Control-Allow-Origin', cors)
            ],
            content_type='text/event-stream; charset=utf-8',
            use_gzip=False
        )
