import asyncio
from typing import Iterable, Any, Optional
from slinn.net.tcp import TcpServer, TcpPipe
from slinn.net.http import HttpRouter, HttpRequest
from slinn.net.address import Address
from slinn.exceptions import SocketClosed
from slinn.utils import optional
import logging
import ssl
import inspect


class HttpServer(TcpServer):
    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, Any],
        routers: Iterable[HttpRouter],
        logger: logging.Logger,
        ssl_context: Optional[ssl.SSLContext] = None
    ) -> None:
        super().__init__(
            address = address,
            protocols_config = protocols_config,
            routers = routers,
            logger = logger,
            ssl_context = ssl_context
        )

        self.http_config = protocols_config.get('http', {})

        self._max_requests = self.http_config.get('max_requests', 200)
        self._max_header_size = self.http_config.get('max_header_size', 8192)

    async def handle_pipe(
        self,
        client_pipe: TcpPipe,
        client_address: Address,
        args: dict[Any, Any]
    ) -> None:
        loop = asyncio.get_event_loop()
        args['max_requests'] = args.get('max_requests', self._max_requests)
        client_pipe.set_timeout(min(self._max_timeout, args.get('timeout', self._timeout)))
        self.logger.debug(f'New HTTP connection from {client_address.host}:{client_address.port} established')
        while not client_pipe.closed:
            args['max_requests'] -= 1
            try:
                if not args['max_requests']:
                    client_pipe.close()
                    break
                try:
                    data = bytearray()
                    while b'\r\n\r\n' not in data:
                        b = await client_pipe.recv(self._max_bytes_per_receive)
                        data += b
                        if not b:
                            break
                    data = data.split(b'\r\n\r\n')
                    header = data[0].decode()
                    client_pipe.paste(b'\r\n\r\n'.join(data[1:]))
                    request = HttpRequest(loop, header, client_address, client_pipe, self)
                    self.logger.info(repr(request))
                except KeyError:
                    self.logger.info('Got KeyError, probably invalid request. Ignore')
                    continue
                except UnicodeDecodeError:
                    self.logger.info('Got UnicodeDecodeError, probably invalid header. Ignore')
                    continue
                endpoints = []
                for router in self.routers:
                    endpoints += router.endpoints
                sizes = [
                    await optional(
                        endpoint.filter.size,
                        client_pipe = client_pipe,
                        client_address = client_address,
                        request = request
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
                    request = request,
                    client_pipe = client_pipe,
                    client_address = client_address,
                    **args
                )
                if inspect.isasyncgenfunction(endpoint.function):
                    async for response in coro:
                        if response:
                            await client_pipe.send(response.make())
                else:
                    response = await coro
                    if response:
                        await client_pipe.send(response.make(version=request.version))

                await request.body.skip()

                if request.connection == 'close':
                    client_pipe.close()
                    continue

            except KeyboardInterrupt:
                raise
            except (SocketClosed, TimeoutError):
                continue
            except Exception as exception:
                self.logger.warning(f'During handling pipe, an {exception} has occurred', exc_info=True)
                await self.reload(*self.routers)
                continue
        self.logger.debug(f'HTTP connection from {client_address.host}:{client_address.port} closed')
