from typing import Iterable, Any, Optional
from slinn.net.address import Address
from slinn.net.tcp import TcpPipe, TcpRouterProtocol
from slinn.exceptions import SocketClosed
from slinn.utils import optional
import logging
import asyncio
import socket
import ssl
import inspect


class TcpServer:
    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, Any],
        routers: Iterable[TcpRouterProtocol],
        logger: logging.Logger,
        ssl_context: Optional[ssl.SSLContext] = None
    ) -> None:
        self.address: Address = address
        self.tcp_config: dict[str, Any] = protocols_config.get('tcp', {})
        self.routers: Iterable[TcpRouterProtocol] = routers
        self.logger: logging.Logger = logger
        self.ssl_context: Optional[ssl.SSLContext] = ssl_context

        self.server_pipe: Optional[TcpPipe] = None

        self._timeout = self.tcp_config.get('timeout', 0.5)
        self._max_timeout = self.tcp_config.get('_max_timeout', 60)
        self._max_bytes_per_receive = self.tcp_config.get('_max_bytes_per_receive', 65535)

    async def reload(self, *routers: TcpRouterProtocol) -> None:
        self.routers = routers
        self.logger.info(f'Server {self.address.host}:{self.address.port} has reloaded')

    async def listen(self) -> None:
        loop = asyncio.get_running_loop()
        self.server_pipe = TcpPipe(
            loop,
            family = self.address.family,
            type = socket.SOCK_STREAM,
            ssl_context = self.ssl_context,
            timeout = min(self._timeout, self._max_timeout),
            bytes_per_receive = self._max_bytes_per_receive
        )
        self.server_pipe.set_sock_opt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_pipe.bind((self.address.host, self.address.port))
        except PermissionError:
            self.logger.critical(f'Permission denied to bind {self.address.host}:{self.address.port}')
            exit(13)
        self.server_pipe.listen()
        self.logger.info(f'Server started to listening {self.address.host}:{self.address.port}')
        while True:
            try:
                client_pipe, client_address = await self.server_pipe.accept()
                loop.create_task(self.handle_pipe(client_pipe, client_address, {}))
            except KeyboardInterrupt:
                await self.shutdown()
                raise
            except (BlockingIOError, socket.timeout):
                await asyncio.sleep(0.005)
            except Exception as e:
                self.logger.warning(f'During handling exception, an {e} has occurred', exc_info=True)
                await self.reload(*self.routers)


    async def handle_pipe(
        self,
        client_pipe: TcpPipe,
        client_address: Address,
        args: dict[Any, Any]
    ) -> None:
        client_pipe.set_timeout(min(self._max_timeout, args.get('timeout', self._timeout)))
        self.logger.info(f'New TCP connection from {client_address.host}:{client_address.port} established')
        while not client_pipe.closed:
            try:
                endpoints = []
                for router in self.routers:
                    endpoints += router.endpoints
                sizes = [
                    await optional(
                        endpoint.filter.size,
                        client_pipe = client_pipe,
                        client_address = client_address
                    )
                    for endpoint in endpoints
                ]
                if not sizes:
                    await client_pipe.recv()
                    continue
                endpoint = endpoints[sizes.index(max(sizes))]
                if max(sizes) < 0:
                    await client_pipe.recv()
                    continue
                coro = optional(
                    endpoint.function,
                    client_pipe = client_pipe,
                    client_address = client_address,
                    **args
                )
                if inspect.isasyncgenfunction(endpoint.function):
                    async for response in coro:
                        if response:
                            await client_pipe.send(response)
                else:
                    response = await coro
                    if response:
                        await client_pipe.send(response)

            except KeyboardInterrupt:
                raise
            except SocketClosed:
                continue
            except Exception as exception:
                self.logger.warning(f'During handling pipe, an {exception} has occurred', exc_info=True)
                await self.reload(*self.routers)
                continue
        self.logger.info(f'TCP connection from {client_address.host}:{client_address.port} closed')

    async def shutdown(self) -> None:
        if not self.server_pipe.closed:
            self.server_pipe.close()
        self.logger.info(f'Server {self.address.host}:{self.address.port} has shut down')
