import asyncio
from typing import Iterable, Any
from slinn.net.tcp import TcpServer, TcpPipe, BaseTcpBus
from slinn.net.tcp.events import DataReceived
from slinn.net.http import HttpRouter, HttpHeaders, HttpRequest, HttpRequestBody, HCRouter, FTRouter, HttpBus
from slinn.net.http.events import HttpRequestReceived
from slinn.net.address import Address
from slinn.net import ServerProtocol
from slinn.eda import on
lazy from slinn.api import ProjectApi, AppApi
from slinn.tools.manage.misc import load_module
from slinn import _
import logging
import ssl
import os


class HttpServer(ServerProtocol):
    class _TcpBus(BaseTcpBus):
        def __init__(
            self,
            max_requests: int,
            routers: Iterable[HttpRouter],
            file_types_router: FTRouter,
            http_codes_router: HCRouter,
            logger: logging.Logger
        ):
            super().__init__()
            self.max_requests = max_requests
            self.routers = routers
            self.file_types_router = file_types_router
            self.http_codes_router = http_codes_router
            self.logger = logger
            self.buffer = bytearray()
        
        @on(DataReceived())
        async def on_data_received(self, data: bytes, client_pipe: TcpPipe, client_address: Address):
            if not hasattr(self.on_data_received.__func__, 'context'):
                self.on_data_received.__func__.context = {}
            if client_pipe not in self.on_data_received.__func__.context:
                self.on_data_received.__func__.context[client_pipe] = {
                    'requests_left': self.max_requests,
                    'bus': HttpBus(
                        routers = self.routers,
                        file_types_router = self.file_types_router,
                        http_codes_router = self.http_codes_router
                    )
                }
            if self.on_data_received.__func__.context[client_pipe]['requests_left'] < 1:
                client_pipe.close()
                return
            
            loop = asyncio.get_running_loop()
            t1 = loop.time()
            self.buffer.extend(data)
            if b'\r\n\r\n' not in self.buffer:
                return
            try:
                buffer, self.buffer = self.buffer.split(b'\r\n\r\n'), bytearray()
                def _repr(request) -> str:
                    return _('[{method}] request {link} from {client_addr} on {authority}').format(
                        method = request.headers.method,
                        link = request.headers.path,
                        client_addr = ('' if '.' in request.client_address.host else '[') +
                                        (request.client_address.host) +
                                        ('' if '.' in request.client_address.host else ']') +
                                        ':' +
                                        str(request.client_address.port),
                        authority = request.headers.authority
                    )
                client_pipe.paste(b'\r\n\r\n'.join(buffer[1:]))
                _headers = HttpHeaders.parse(buffer[0])
                request = HttpRequest(
                    client_address, _headers, HttpRequestBody(_headers, client_pipe)
                )
                t2 = loop.time()
                #self.logger.info(_repr(request))
                t3 = loop.time()
                await self.on_data_received.__func__.context[client_pipe]['bus'].dispatch(
                    HttpRequestReceived(),
                    request = request,
                    client_pipe = client_pipe,
                    client_address = client_address,
                    extend_headers = HttpHeaders(default_headers={
                        'Server-Timing': ((
                            f'parse;desc="Parsing request";dur={(t2-t1)*1000},'
                            f'log;desc="Logging request";dur={(t3-t2)*1000},'
                        ), )
                    })
                )
            except KeyError:
                self.logger.info(_('Got KeyError, probably invalid request. Ignore'))
                client_pipe.close()
            except UnicodeDecodeError:
                self.logger.info(_('Got UnicodeDecodeError, probably invalid header. Ignore'))
                client_pipe.close()
            

    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, dict[str, Any]],
        logger: logging.Logger,
        buses: Iterable[HttpBus] | None = None,
        ssl_context: ssl.SSLContext | None = None
    ) -> None:
        self.logger = logger

        self.http_config = protocols_config.get('http', {})

        self._max_requests = self.http_config['max_requests']
        self._max_header_size = self.http_config['max_header_size']

        self.project = ProjectApi(os.getcwd())
        self.project.load_config()
        self.routers = [*app.load_http_routers() for app in self.project.load_apps()]
        
        self._http_codes_router = HCRouter()
        if 'http_codes_router' in self.http_config:
            *mod, obj =  self.http_config['http_codes_router'].split('.')
            self._http_codes_router = getattr(load_module('/'.join(mod)+'.py'), obj)

        self._file_types_router = FTRouter()
        if 'file_types_router' in self.http_config:
            *mod, obj =  self.http_config['file_types_router'].split('.')
            self._file_types_router = getattr(load_module('/'.join(mod)+'.py'), obj)
        
        self.buses = list(buses or (HttpServer._TcpBus(
            max_requests = self._max_requests,
            routers = self.routers,
            file_types_router = self._file_types_router,
            http_codes_router = self._http_codes_router,
            logger = self.logger
        ), ))
        
        self._server = TcpServer(
            address = address,
            protocols_config = protocols_config,
            logger = logger,
            buses = self.buses,
            ssl_context = ssl_context,
        )
        
        self.handle_pipe = self._server.handle_pipe
        self.shutdown = self._server.shutdown

    async def reload(self, *routers: HttpRouter) -> None:
        self.routers = routers
        await self._server.reload()

    async def listen(self):
        await self._server.listen()
