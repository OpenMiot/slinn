from typing import Iterable, Any
from slinn.net import ServerProtocol
from slinn.net.address import Address
from slinn.net.tcp import TcpServer
from slinn.net.http import HttpServer, HttpRouter
from slinn.eda import BaseBus
from slinn import _
from dataclasses import dataclass
import threading
import asyncio
import logging
import sys


def get_loop_factory():
    if sys.platform == 'win32':
        try:
            import winloop
            return winloop.new_event_loop
        except ImportError:
            return asyncio.SelectorEventLoop
    else:
        try:
            import uvloop
            return uvloop.new_event_loop
        except ImportError:
            return asyncio.new_event_loop


def server_factory(
    address: Address,
    protocols: dict[str, Protocol],
    buses: Iterable,
    protocols_config: dict[str, Any],
    logger: logging.Logger
) -> ServerProtocol:
    protocol = protocols[address.protocol]
    return protocol.server_class(
        address,
        protocols_config,
        logger,
        None,
        None
    )


@dataclass(frozen=True)
class Protocol:
    protocol_name: str
    server_class: type[ServerProtocol]
    bus_class: type[BaseBus]


class Dispatcher:
    def __init__(
        self,
        addresses: Iterable[Address],
        routers: Iterable,
        protocols_config: dict[str, Any],
        logger: logging.Logger,
    ):
        self.addresses = addresses
        self.routers = routers
        self.protocols_config = protocols_config
        self.protocols = {}
        self.logger: logging.Logger = logger

        self._main_thread: threading.Thread = threading.main_thread()

        #self.register_protocol('tcp', TcpServer, TcpRouterProtocol)
        self.register_protocol('http', HttpServer, None)

    def register_protocol(
        self,
        protocol_name: str,
        server_class: type[ServerProtocol],
        bus_class: type[BaseBus]
    ):
        self.protocols[protocol_name] = Protocol(protocol_name, server_class, bus_class)

    def start(self):
        def run_servers():
            async def main():
                coros = []
                for address in self.addresses:
                    server = server_factory(address, self.protocols, self.routers, self.protocols_config, self.logger)
                    coros.append(server.listen())
                await asyncio.gather(*coros)
            event_loop = get_loop_factory()()
            asyncio.set_event_loop(event_loop)
            event_loop.run_until_complete(main())
            try:
                event_loop.run_until_complete(main())
            finally:
                try:
                    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
                finally:
                    event_loop.close()

        self._main_thread = threading.Thread(target=run_servers, daemon=False)
        self._main_thread.start()

    def join(self):
        self._main_thread.join()

    def print_servers(self):
        for address in self.addresses:
            print(
                _('{protocol} server on {transport_protocol}/{port} is available at:').format(
                    protocol = address.protocol.upper(),
                    transport_protocol = address.transport_protocol.value,
                    port = address.port,
                )
            )
            print(*[f'  - {url}' for url in str(address).split()], sep='\n')
