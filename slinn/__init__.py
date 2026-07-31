import os
import sys
import inspect
import warnings
from datetime import datetime, timedelta
from string import ascii_uppercase
from .address import Address
from .endpoint import Endpoint
from .i_middleware import IMiddleware
from .preprocessor import Preprocessor
from .tcp_response_chunk import TCPResponseChunk
from .http_response_chunk import HttpResponseChunk
from .http_response_header import CookieSameSite
from .http_response_header import HttpResponseHeader
from .websocket_opcodes import WebSocketOpcodes
from .websocket_handshake import WebSocketHandshake
from .websocket_frame import WebSocketFrame
from .websocket_connection import WebSocketConnection
from .websocket_group import WebSocketGroup
from .filter import Filter
from .link_filter import LinkFilter
from .any_filter import AnyFilter
from .hcdispatcher import HCDispatcher
from .ftdispatcher import FTDispatcher
from .socket_wrapper import SocketWrapper
from .ssl_socket_wrapper import SSLSocketWrapper
from .request import Request, RequestBody
from .i_path import IPath
from .path import Path
from .router import Router
from .http_response import HttpResponse
from .http_redirect import HttpRedirect
from .http_get_redirect import HttpGETRedirect
from .empty_http_response import EmptyHttpResponse
from .http_render import HttpRender
from .http_api_response import HttpAPIResponse
from .http_json_response import HttpJSONResponse
from .http_json_api_response import HttpJSONAPIResponse
from .sse_header import SSEHeader
from .sse_event import SSEEvent
from .server import Server
from .storage import Storage, StorageIO
from .migration import Migration
from .template_protocol import TemplateProtocol
from . import utils


__PD, __PI = datetime(2026, 8, 1), 2

VERSION = {
    'name': 'Slinn',
    'codename': 'Flux',
    'version': {
        'major': 3,
        'minor': 0,
        'patch': 0,
        'type': 'alpha',
        'revision': 2
    },
    'version_id': __PD.strftime('%d%m%y') + ascii_uppercase[__PI - 1],
    'dies_at': __PD + timedelta(days=120),
    'is_snapshot': False,
    'may_incompatible': False
}
make_version = lambda ver: f'{ver['major']}.{ver['minor']}.{ver['patch']}' + (
    f'{ver['type'][0]}{ver['revision']}' if ver['revision'] else '')
version = f'{VERSION['name']} {VERSION['codename']} {make_version(VERSION['version'])}'

root = os.path.dirname(inspect.getfile(sys.modules[__name__]))
slinn_root = Storage(root)


from .project_api import ProjectAPI
from .slinn_app_api import SlinnAppAPI


warnings.simplefilter('always', DeprecationWarning)

if VERSION['is_snapshot'] and datetime.now() > VERSION['dies_at']:
    exit("Slinn`s version has expired. You need to upgrade")

if VERSION['may_incompatible']:
    warnings.warn('Slinn`s version may be incompatible with future releases. DO NOT use it in prod')
