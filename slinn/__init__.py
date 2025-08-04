import warnings
from datetime import datetime
from .address import Address
from .handle import Handle
from .i_middleware import IMiddleware
from .file import File
from .preprocessor import Preprocessor
from .filter import Filter
from .link_filter import LinkFilter
from .any_filter import AnyFilter
from .dispatcher import Dispatcher
from .hcdispatcher import HCDispatcher
from .ftdispatcher import FTDispatcher
from .request import Request
from .async_request import AsyncRequest
from .i_path import IPath
from .path import Path
from .tcp_response_chunk import TCPResponseChunk
from .http_response_chunk import HttpResponseChunk
from .http_response_header import HttpResponseHeader
from .http_response import HttpResponse
from .http_redirect import HttpRedirect
from .empty_http_response import EmptyHttpResponse
from .http_render import HttpRender
from .http_api_response import HttpAPIResponse
from .http_json_response import HttpJSONResponse
from .http_json_api_response import HttpJSONAPIResponse
from .sse_header import SSEHeader
from .sse_event import SSEEvent
from .websocket_opcodes import WebSocketOpcodes
from .websocket_handshake import WebSocketHandshake
from .websocket_frame import WebSocketFrame
from .async_websocket_connection import AsyncWebSocketConnection
from .async_socket_wrapper import AsyncSocketWrapper
from .async_ssl_socket_wrapper import AsyncSSLSocketWrapper
from .server import Server
from .async_server import AsyncServer
from .api_dispatcher import ApiDispatcher
from .storage import Storage, StorageIO
from . import utils


VERSION = {
    'name': 'Slinn',
    'codename': 'Nukeful',
    'version': '2.3.1',
    'version_id': '040725A',
    'dies_at': datetime(2025, 9, 2, 23, 59)
}
version = '{} {} v{} {}'.format(*list(VERSION.values())[:-1])

Response = HttpResponse
ResponseHeader = HttpResponseHeader
ResponseChunk = HttpResponseChunk
Redirect = HttpRedirect
EmptyResponse = EmptyHttpResponse
Render = HttpRender
APIResponse = HttpAPIResponse
JSONResponse = HttpJSONResponse
JSONAPIResponse = HttpJSONAPIResponse

HttpResponse = utils.make_deprecated(HttpResponse, Response)
HttpRedirect = utils.make_deprecated(HttpRedirect, Redirect)
EmptyHttpResponse = utils.make_deprecated(EmptyHttpResponse, EmptyResponse)
HttpRender = utils.make_deprecated(HttpRender, Render)
HttpAPIResponse = utils.make_deprecated(HttpAPIResponse, APIResponse)
HttpJSONResponse = utils.make_deprecated(HttpJSONResponse, JSONResponse)
HttpJSONAPIResponse = utils.make_deprecated(HttpJSONAPIResponse, JSONAPIResponse)

warnings.simplefilter('always', DeprecationWarning)

if datetime.now() > VERSION['dies_at']:
    exit("Slinn`s version has expired. You need to upgrade")
