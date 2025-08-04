from . import HttpResponseHeader, HttpResponseChunk


class HttpResponse(HttpResponseHeader, HttpResponseChunk):
    """
    Base class for all responses
    """

    def __init__(self, payload: any, data: list[tuple] = None, status: str = '200 OK',
                 content_type: str = 'text/plain; charset=utf-8') -> None:
        HttpResponseHeader.__init__(self, data, status, content_type)
        HttpResponseChunk.__init__(self, payload)
