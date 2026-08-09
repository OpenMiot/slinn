import asyncio
from typing import Iterable, Any, Optional
from slinn.net.tcp import TcpServer, TcpPipe, TcpRouterProtocol
from slinn.net.http import HttpRouter, HttpRequest
from slinn.net.address import Address
from slinn.net import ServerProtocol, FilterProtocol, Endpoint
from slinn.utils import optional
from slinn import _
import functools
import logging
import ssl
import inspect


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
        ssl_context: Optional[ssl.SSLContext] = None
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
            loop = asyncio.get_event_loop()
            args = {}
            while not client_pipe.closed:
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
                            b = await client_pipe.recv(self._server.max_bytes_per_receive)
                            data += b
                            if not b:
                                break
                        except (asyncio.CancelledError, TimeoutError):
                            break
                    data = data.split(b'\r\n\r\n')
                    header = data[0].decode()
                    if not header:
                        continue
                    client_pipe.paste(b'\r\n\r\n'.join(data[1:]))
                    request = HttpRequest(loop, header, client_address, client_pipe, self)
                    self.logger.info(repr(request))
                except KeyError:
                    self.logger.info(_('Got KeyError, probably invalid request. Ignore'))
                    continue
                except UnicodeDecodeError:
                    self.logger.info(_('Got UnicodeDecodeError, probably invalid header. Ignore'))
                    continue
                endpoints = []
                for router in self.routers:
                    if optional(
                            router.check,
                            client_pipe=client_pipe,
                            client_address=client_address,
                            request=request
                    ):
                        endpoints += router.endpoints
                sizes = [
                    await optional(
                        endpoint.filter.size,
                        client_pipe=client_pipe,
                        client_address=client_address,
                        request=request
                    )
                    for endpoint in endpoints
                ]
                if not sizes:
                    continue
                endpoint = endpoints[sizes.index(max(sizes))]
                if max(sizes) < 0:
                    continue
                coro = optional(
                    endpoint.function,
                    request=request,
                    client_pipe=client_pipe,
                    client_address=client_address,
                    **args
                )
                if inspect.isasyncgenfunction(endpoint.function):
                    async for response in coro:
                        if response:
                            yield response.make(request=request)
                else:
                    response = await coro
                    if response:
                        yield response.make(request=request)

                await request.body.skip()

                if request.connection == 'close':
                    client_pipe.close()
                    return

    async def reload(self, *routers: TcpRouterProtocol) -> None:
        self.routers = routers
        await self._server.reload()
