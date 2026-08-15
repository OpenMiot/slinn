import asyncio
from typing import Iterable, Any
from slinn.net.tcp import TcpServer, TcpPipe, TcpRouterProtocol
from slinn.net.http import HttpRouter, HttpVersion, HttpHeaders, HttpRequestBody
from slinn.net.http.exceptions import HttpHeaderAlreadySent
from slinn.net.http.responses import HttpResponse, HttpChunkResponse, HttpHeaderResponse
from slinn.net.address import Address
from slinn.net import ServerProtocol, FilterProtocol, Endpoint
from slinn.utils import optional
from slinn import _
import functools
import logging
import ssl
import inspect
import io


class HttpServer(ServerProtocol):
    class _TcpAnyFilter(FilterProtocol):
        async def size(self) -> int:
            return 0

        def args(self) -> dict:
            return {}

    class _TcpRouter(TcpRouterProtocol):
        def __init__(self):
            self.endpoints: list[Endpoint] = []

        def __call__(self, request_filter: HttpServer._TcpAnyFilter):
            def decorator(func):
                if inspect.isasyncgenfunction(func):
                    @functools.wraps(func)
                    async def wrapper(*args, **kwargs):
                        async for item in func(*args, **kwargs):
                            yield item
                else:
                    @functools.wraps(func)
                    async def wrapper(*args, **kwargs):
                        return await func(*args, **kwargs)

                self.endpoints = [Endpoint(request_filter, wrapper, request_filter.args)]
                return wrapper

            return decorator

        def check(self, *args, **kwargs) -> bool:
            return True

    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, dict[str, Any]],
        routers: Iterable[HttpRouter],
        logger: logging.Logger,
        ssl_context: ssl.SSLContext | None = None
    ) -> None:
        self.routers = routers
        self.logger = logger

        self._router = HttpServer._TcpRouter()
        self._server = TcpServer(
            address=address,
            protocols_config=protocols_config,
            routers=(self._router, ),
            logger=logger,
            ssl_context=ssl_context
        )

        self.http_config = protocols_config.get('http', {})

        self._max_requests = self.http_config.get('max_requests', 1000)
        self._max_header_size = self.http_config.get('max_header_size', 8192)

        self.listen = self._server.listen
        self.handle_pipe = self._server.handle_pipe
        self.shutdown = self._server.shutdown

        @self._router(HttpServer._TcpAnyFilter())
        async def http_endpoint(client_pipe: TcpPipe, client_address: Address):
            loop = asyncio.get_running_loop()
            args = {}
            while not client_pipe.closed:
                t0 = loop.time()
                args['max_requests'] = args.get('max_requests', self._max_requests)
                client_pipe.set_timeout(min(self._server.max_timeout, args.get('timeout', self._server.timeout)))
                args['max_requests'] -= 1
                if not args['max_requests']:
                    client_pipe.close()
                    return
                try:
                    data = bytearray()
                    while b'\r\n\r\n' not in data:
                        try:
                            chunk = await client_pipe.recv(self._server.max_bytes_per_receive)
                            data.extend(chunk)
                            if not chunk or not data:
                                break
                        except asyncio.CancelledError, TimeoutError:
                            break
                    t1 = loop.time()
                    if not data:
                        continue
                    data = data.split(b'\r\n\r\n')
                    def _repr(hd) -> str:
                        return _('[{method}] request {link} from {client_addr} on {authority}').format(
                            method = hd.method,
                            link = hd.path,
                            client_addr = ('' if '.' in client_address.host else '[') +
                                            (client_address.host) +
                                            ('' if '.' in client_address.host else ']') +
                                            ':' +
                                            str(client_address.port),
                            authority = hd.authority
                        )
                    client_pipe.paste(b'\r\n\r\n'.join(data[1:]))
                    headers = HttpHeaders.parse(data[0])
                    body = HttpRequestBody(headers, client_pipe)
                    t2 = loop.time()
                    #self.logger.info(_repr(headers))
                    t3 = loop.time()
                    #request = HttpRequest(loop, header, client_address, client_pipe, self)
                except KeyError:
                    self.logger.info(_('Got KeyError, probably invalid request. Ignore'))
                    continue
                except UnicodeDecodeError:
                    self.logger.info(_('Got UnicodeDecodeError, probably invalid header. Ignore'))
                    continue
                endpoints = []
                meta = frozendict(
                    client_pipe = client_pipe,
                    client_address = client_address,
                    headers = headers,
                    body = body
                )
                """for router in self.routers:
                    if optional(router.check, **meta):
                        endpoints += router.endpoints
                sizes = [
                    await optional(endpoint.filter.size, **meta)
                    for endpoint in endpoints
                ]
                if not sizes:
                    continue
                endpoint = endpoints[sizes.index(max(sizes))]
                if max(sizes) < 0:
                    continue"""
                endpoint = self.routers[0].endpoints[2]
                t4 = loop.time()
                resp_headers = await handle_endpoint(endpoint, meta | args, HttpHeaders(default_headers = {
                    'Server-Timing': (
                        f'recv;dur={(t1-t0)*1000},parse;dur={(t2-t1)*1000},log;dur={(t3-t2)*1000},route;dur={(t4-t3)*1000}', 
                    )
                }), client_pipe)
                t5 = loop.time()

                await body.skip()
                t6 = loop.time()

                if resp_headers and 'chunked' in resp_headers.get('Transfer-Encoding', ()):
                    await client_pipe.send(b'0\r\n')
                    await client_pipe.send(f'Server-Timing: endpoint;dur={(t5-t4)*1000},skip;dur={(t6-t5)*1000}\r\n'.encode())
                    await client_pipe.send(b'\r\n')
                
                if resp_headers.get('Connection', 'close' if resp_headers.version is HttpVersion.H1 else 'Keep-Alive') == 'close':
                    client_pipe.close()
                    return

        async def handle_endpoint(endpoint: Endpoint, args: frozendict, add_headers: HttpHeaders, client_pipe: TcpPipe) -> HttpHeaders:
            coro = optional(endpoint.function, **args)
            if not endpoint.is_generator:
                return await answer_response(await coro, args['headers'], None, add_headers, client_pipe)
            resp_headers: HttpHeaders | None = None
            async for response in coro:
                resp_headers = await answer_response(response, args['headers'], resp_headers, add_headers, client_pipe)

        async def answer_response(
            response: Any,
            recv_headers: HttpHeaders,
            resp_headers: HttpHeaders,
            add_headers: HttpHeaders,
            client_pipe: TcpPipe
        ) -> HttpHeaders:
            if not response:
                return
            if not isinstance(response, HttpChunkResponse):
                response = HttpResponse(response)
            if isinstance(response, HttpHeaderResponse):
                if resp_headers:
                    raise HttpHeaderAlreadySent()
                resp_headers = add_headers
                if recv_headers.version == HttpVersion.H11:
                    resp_headers.add_many({
                        'Trailer': ('Server-Timing', ),
                        'Transfer-Encoding': ('chunked', )
                    })
                response.headers.extend(resp_headers)
                await client_pipe.send(response.make_headers(recv_headers))
            made = response.make(recv_headers)
            if resp_headers and 'chunked' in resp_headers.get('Transfer-Encoding', ()):
                await client_pipe.send(b''.join((hex(len(made))[2:].upper().encode(), b'\r\n', made, b'\r\n')))
            else:
                await client_pipe.send(made)
            return resp_headers

    async def reload(self, *routers: TcpRouterProtocol) -> None:
        self.routers = routers
        await self._server.reload()
