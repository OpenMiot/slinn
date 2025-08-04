from .http_response import HttpResponse
import slinn


class HttpAPIResponse(HttpResponse):
    
    """
    Like HttpResponse, but with header `Access-Control-Allow-Origin: *`
    """

    def __init__(self, payload: any, data: list[tuple] = None, status: str = '200 OK',
                 content_type: str = 'text/plain; charset=utf-8') -> None:
        self.payload = slinn.utils.representate(payload)
        self.content_type = content_type
        default_data = [('Server', 'Slinn'), ('Content-Type', content_type), ('Access-Control-Allow-Origin', '*')]
        self.data = default_data + data if data is not None else default_data + [('Content-Length', len(self.payload))]
        self.status = status
