from datetime import datetime, timedelta
from functools import partial
from slinn import utils
import os
import sys
import inspect
import warnings


__getattr__ = partial(utils.lazy_exporter, __name__, {
    'Endpoint': 'endpoint',
    'IMiddleware': 'i_middleware',
    'Preprocessor': 'preprocessor',
    'TCPResponseChunk': 'tcp_response_chunk',
    'HttpResponseChunk': 'http_response_chunk',
    'CookieSameSite': 'http_response_header',
    'HttpResponseHeader': 'http_response_header',
    'WebSocketOpcodes': 'websocket_opcodes',
    'WebSocketHandshake': 'websocket_handshake',
    'WebSocketFrame': 'websocket_frame',
    'WebSocketConnection': 'websocket_connection',
    'WebSocketGroup': 'websocket_group',
    'Filter': 'filter',
    'LinkFilter': 'link_filter',
    'AnyFilter': 'any_filter',
    'HCDispatcher': 'hcdispatcher',
    'FTDispatcher': 'ftdispatcher',
    'SocketWrapper': 'socket_wrapper',
    'SSLSocketWrapper': 'ssl_socket_wrapper',
    'Request': 'request',
    'RequestBody': 'request',
    'IPath': 'i_path',
    'Path': 'path',
    'Router': 'router',
    'HttpResponse': 'http_response',
    'HttpRedirect': 'http_redirect',
    'HttpGETRedirect': 'http_get_redirect',
    'EmptyHttpResponse': 'empty_http_response',
    'HttpRender': 'http_render',
    'HttpAPIResponse': 'http_api_response',
    'HttpJSONResponse': 'http_json_response',
    'HttpJSONAPIResponse': 'http_json_api_response',
    'SSEHeader': 'sse_header',
    'SSEEvent': 'sse_event',
    'Server': 'server',
    'Migration': 'migration',
    'TemplateProtocol': 'template_protocol',
})


__PD = datetime(2026, 8, 2)

VERSION = {
    'name': 'Slinn',
    'codename': 'Flux',
    'version': {
        'major': 3,
        'minor': 0,
        'patch': 0,
        'type': 'alpha',
        'revision': 3
    },
    'dies_at': __PD + timedelta(days=180),
    'is_snapshot': True,
    'may_incompatible': True
}
make_version = lambda ver: f'{ver['major']}.{ver['minor']}.{ver['patch']}' + (
    f'{ver['type'][0]}{ver['revision']}' if ver['revision'] else '')
version = f'{VERSION['name']} {VERSION['codename']} {make_version(VERSION['version'])}'

root = os.path.dirname(inspect.getfile(sys.modules[__name__]))


warnings.simplefilter('always', DeprecationWarning)

if VERSION['is_snapshot'] and datetime.now() > VERSION['dies_at']:
    exit("Slinn`s version has expired. You need to upgrade")

if VERSION['may_incompatible']:
    warnings.warn('Slinn`s version may be incompatible with future releases. DO NOT use it in prod')
