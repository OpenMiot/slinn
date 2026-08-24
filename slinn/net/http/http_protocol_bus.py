from slinn.net.http import HttpRouter, FTRouter, HCRouter, HttpRequestBus, HttpHeaders, HttpRequest, HttpRequestBody
from slinn.net.http.events import HttpRequestReceived
from slinn.net.tcp import BaseTcpBus, TcpPipe
from slinn.net.tcp.events import DataReceived
from slinn.net.address import Address
from slinn.eda import on
from slinn import _
from collections.abc import Iterable
import logging
import time


class HttpProtocolBus(BaseTcpBus):
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
                    'bus': HttpRequestBus(
                        routers = self.routers,
                        file_types_router = self.file_types_router,
                        http_codes_router = self.http_codes_router
                    )
                }
            if self.on_data_received.__func__.context[client_pipe]['requests_left'] < 1:
                client_pipe.close()
                return
            
            t1 = time.perf_counter_ns()
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
                t2 = time.perf_counter_ns()
                #self.logger.info(_repr(request))
                t3 = time.perf_counter_ns()
                await self.on_data_received.__func__.context[client_pipe]['bus'].dispatch(
                    HttpRequestReceived(),
                    request = request,
                    client_pipe = client_pipe,
                    client_address = client_address,
                    extend_headers = HttpHeaders(default_headers={
                        'Server-Timing': ((
                            f'parse;desc="Parsing request";dur={(t2-t1)*1e-6},'
                            f'log;desc="Logging request";dur={(t3-t2)*1e-6},'
                        ), )
                    })
                )
            except KeyError:
                self.logger.info(_('Got KeyError, probably invalid request. Ignore'))
                client_pipe.close()
            except UnicodeDecodeError:
                self.logger.info(_('Got UnicodeDecodeError, probably invalid header. Ignore'))
                client_pipe.close()