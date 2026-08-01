from slinn.utils import lazy_exporter
from functools import partial


__getattr__ = partial(lazy_exporter, __name__, {
    'HTTPClient': 'http_client',
    'HTTPFilter': 'http_filter',
    'HTTPRequest': 'http_request',
    'HTTPResponse': 'http_response',
    'HTTPRouter': 'http_router',
    'HTTPServer': 'http_server',
})
