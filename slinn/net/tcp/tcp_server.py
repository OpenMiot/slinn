from typing import Iterable, Any
from slinn.net.address import Address
from slinn.net.tcp import TcpPipe, TcpRouterProtocol
from slinn.exceptions import SocketClosed
from slinn.utils import optional
from slinn import _
import logging
import asyncio
import socket
import ssl
import inspect
import os


class TcpServer:
    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, dict[str, Any]],
        routers: Iterable[TcpRouterProtocol],
        logger: logging.Logger,
        ssl_context: ssl.SSLContext | None = None
    ) -> None:
        self.address: Address = address
        self.tcp_config: dict[str, Any] = protocols_config.get('tcp', {})
        self.routers: Iterable[TcpRouterProtocol] = routers
        self.logger: logging.Logger = logger
        self.ssl_context: ssl.SSLContext | None = ssl_context

        self.server_pipes: list[TcpPipe] = []
        self.waiting_pipes: dict = {}

        self.timeout = self.tcp_config.get('timeout', 0.5)
        self.max_timeout = self.tcp_config.get('_max_timeout', 60)
        self.max_bytes_per_receive = self.tcp_config.get('_max_bytes_per_receive', 65535)

        self.debounce = 0.005

    async def reload(self, *routers: TcpRouterProtocol) -> None:
        self.routers = routers
        self.logger.info(f'Server :{self.address.port} has reloaded')

    async def listen(self) -> None:
        event_loop = asyncio.get_running_loop()
        for family, ip in self.address.ips.items():
            server_pipe = TcpPipe(
                event_loop,
                family = family,
                type = socket.SOCK_STREAM,
                ssl_context = self.ssl_context,
                timeout = min(self.timeout, self.max_timeout),
                bytes_per_receive = self.max_bytes_per_receive
            )
            server_pipe.set_sock_opt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                server_pipe.bind((ip, self.address.port))
            except PermissionError, OSError:
                message = _('Cannot bind {ip}:{port}').format(
                    ip = ip,
                    port = self.address.port
                )
                self.logger.critical(message)
                print(message)
                os._exit(13)
            server_pipe.listen()
            self.logger.info(_('Server started to listening {ip}:{port}').format(
                ip = ip,
                port = self.address.port
            ))
            self.server_pipes.append(server_pipe)
            event_loop.add_reader(server_pipe.file_no(), self.waiting_pipes.setdefault, server_pipe)
        
        try:
            while True:
                try:
                    while self.waiting_pipes:
                        server_pipe = next(iter(self.waiting_pipes.keys()))
                        client_pipe, client_address = await server_pipe.accept()
                        del self.waiting_pipes[server_pipe]
                        event_loop.create_task(self.handle_pipe(client_pipe, client_address, {}))
                    #self.waiting_pipes = set()
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    self.logger.warning(
                        _('During handling exception, an {exception} has occurred').format(exception = e), exc_info=True
                    )
                    await self.reload(*self.routers)
                await asyncio.sleep(self.debounce)
        except KeyboardInterrupt:
            await self.shutdown()
            raise


    async def handle_pipe(
        self,
        client_pipe: TcpPipe,
        client_address: Address,
        args: dict[Any, Any]
    ) -> None:
        client_pipe.set_timeout(min(self.max_timeout, args.get('timeout', self.timeout)))
        self.logger.debug(f'New TCP connection from {client_address.host}:{client_address.port} established')
        while not client_pipe.closed:
            await asyncio.sleep(self.debounce)
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
                if endpoint.is_generator:
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
        self.logger.debug(f'TCP connection from {client_address.host}:{client_address.port} closed')

    async def shutdown(self) -> None:
        if not self.server_pipe.closed:
            self.server_pipe.close()
        self.logger.info(f'Server {self.address.host}:{self.address.port} has shut down')
        asyncio.get_running_loop().stop()
