import os
import sys
import inspect
import warnings
from datetime import datetime
from .address import Address
from .handle import Handle
from .i_middleware import IMiddleware
from .file import File
from .preprocessor import Preprocessor
from .tcp_response_chunk import TCPResponseChunk
from .http_response_chunk import HttpResponseChunk
from .http_response_header import CookieSameSite
from .http_response_header import HttpResponseHeader
from .websocket_opcodes import WebSocketOpcodes
from .websocket_handshake import WebSocketHandshake
from .websocket_frame import WebSocketFrame
from .websocket_connection import WebSocketConnection
from .async_websocket_connection import AsyncWebSocketConnection
from .websocket_group import WebSocketGroup
from .async_websocket_group import AsyncWebSocketGroup
from .filter import Filter
from .link_filter import LinkFilter
from .any_filter import AnyFilter
from .i_path import IPath
from .path import Path
from .dispatcher import Dispatcher
from .hcdispatcher import HCDispatcher
from .ftdispatcher import FTDispatcher
from .api_dispatcher import ApiDispatcher
from .request import Request, RequestBody
from .async_request import AsyncRequest, AsyncRequestBody
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
from .socket_wrapper import SocketWrapper
from .ssl_socket_wrapper import SSLSocketWrapper
from .async_socket_wrapper import AsyncSocketWrapper
from .async_ssl_socket_wrapper import AsyncSSLSocketWrapper
from .server import Server
from .async_server import AsyncServer
from .storage import Storage, StorageIO
from .migration import Migration
from .template_protocol import TemplateProtocol
from . import utils


VERSION = {
    'name': 'Slinn',
    'codename': 'Nukeful',
    'version': '2.3.2',
    'version_id': '130326A',
    'meta': {
        'dies_at': datetime(2026, 7, 13, 23, 59),
        'is_snapshot': True,
        'may_incompatible': False
    }
}
version = '{} {} v{} {}'.format(*list(VERSION.values())[:-1])

root = os.path.dirname(inspect.getfile(sys.modules[__name__]))
slinn_root = Storage(root)


from .project_api import ProjectAPI


Response = utils.rename_class(HttpResponse, 'Response')
ResponseHeader = utils.rename_class(HttpResponseHeader, 'ResponseHeader')
ResponseChunk = utils.rename_class(HttpResponseChunk, 'ResponseChunk')
Redirect = utils.rename_class(HttpRedirect, 'Redirect')
EmptyResponse = utils.rename_class(EmptyHttpResponse, 'EmptyResponse')
Render = utils.rename_class(HttpRender, 'Render')
APIResponse = utils.rename_class(HttpAPIResponse, 'APIResponse')
JSONResponse = utils.rename_class(HttpJSONResponse, 'JSONResponse')
JSONAPIResponse = utils.rename_class(HttpJSONAPIResponse, 'JSONAPIResponse')

Response = utils.make_deprecated(Response, HttpResponse)
Redirect = utils.make_deprecated(Redirect, HttpRedirect)
EmptyResponse = utils.make_deprecated(EmptyResponse, EmptyHttpResponse)
Render = utils.make_deprecated(Render, HttpRender)
APIResponse = utils.make_deprecated(APIResponse, HttpAPIResponse)
JSONResponse = utils.make_deprecated(JSONResponse, HttpJSONResponse)
JSONAPIResponse = utils.make_deprecated(JSONAPIResponse, HttpJSONAPIResponse)

warnings.simplefilter('always', DeprecationWarning)

if VERSION['meta']['is_snapshot'] and datetime.now() > VERSION['meta']['dies_at']:
    exit("Slinn`s version has expired. You need to upgrade")

if VERSION['meta']['may_incompatible']:
    warnings.warn('Slinn`s version may be incompatible with future releases. DO NOT use it in prod')
