from typing import Iterable, Any
from slinn.net.address import Address
from slinn.net.tcp import TcpPipe, BaseTcpBus
from slinn.net.tcp.events import DataReceived, Accepted
from slinn.exceptions import SocketClosed
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
        logger: logging.Logger,
        buses: Iterable[BaseTcpBus] | None = None,
        ssl_context: ssl.SSLContext | None = None,
    ) -> None:
        self.address: Address = address
        self.tcp_config: dict[str, Any] = protocols_config.get('tcp', {})
        self.logger: logging.Logger = logger
        self.buses = buses or (BaseTcpBus(), )
        self.ssl_context: ssl.SSLContext | None = ssl_context

        self.server_pipes: list[TcpPipe] = []
        self.waiting_pipes: dict = {}

        self.timeout = self.tcp_config.get('timeout', 0.5)
        self.max_timeout = self.tcp_config.get('_max_timeout', 60)
        self.max_bytes_per_receive = self.tcp_config.get('_max_bytes_per_receive', 65535)

        self.debounce = 0.0002

    async def reload(self, *args, **kwargs) -> None:
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
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    self.logger.warning(
                        _('During handling exception, an {exception} has occurred').format(exception = e), exc_info=True
                    )
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
            try:
                try:
                    data = await client_pipe.recv()
                    for bus in self.buses:
                        await bus.dispatch(
                            DataReceived(),
                            data,
                            client_pipe,
                            client_address
                        )
                except TimeoutError:
                    ...
            except KeyboardInterrupt:
                raise
            except SocketClosed:
                continue
            except Exception as exception:
                self.logger.warning(f'During handling pipe, an {exception} has occurred', exc_info=True)
                await self.reload()
                continue
        self.logger.debug(f'TCP connection from {client_address.host}:{client_address.port} closed')

    async def shutdown(self) -> None:
        if not self.server_pipe.closed:
            self.server_pipe.close()
        self.logger.info(f'Server {self.address.host}:{self.address.port} has shut down')
        asyncio.get_running_loop().stop()
