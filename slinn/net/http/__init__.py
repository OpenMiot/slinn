from slinn.utils import lazy_exporter
from functools import partial


__getattr__ = partial(lazy_exporter, __name__, {
    'HttpClient': 'http_client',
    'HttpFilter': 'http_filter',
    'HttpRequest': 'http_request',
    'HttpResponse': 'http_response',
    'HttpRouter': 'http_router',
    'HttpServer': 'http_server',
})
