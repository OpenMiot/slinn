from typing import Iterable, Any, Optional
from slinn.net import ServerProtocol, RouterProtocol
from slinn.net.address import Address
from slinn.net.tcp import TcpServer, TcpRouterProtocol
from slinn.net.http import HttpServer, HttpRouter
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
            return asyncio.new_event_loop
    else:
        try:
            import uvloop
            return uvloop.new_event_loop
        except ImportError:
            return asyncio.new_event_loop


def server_factory(
    address: Address,
    protocols: dict[str, Protocol],
    routers: Iterable[RouterProtocol],
    protocols_config: dict[str, Any],
    logger: logging.Logger
) -> ServerProtocol:
    protocol = protocols[address.protocol]
    return protocol.server_class(
        address,
        protocols_config,
        [
            router
            for router in routers
            if type(router) is protocol.router_class
        ],
        logger,
        None
    )


@dataclass(frozen=True)
class Protocol:
    protocol_name: str
    server_class: type[ServerProtocol]
    router_class: type[RouterProtocol]


class Dispatcher:
    def __init__(
        self,
        addresses: Iterable[Address],
        routers: Iterable[RouterProtocol],
        protocols_config: dict[str, Any],
        logger: logging.Logger,
    ):
        self.addresses = addresses
        self.routers = routers
        self.protocols_config = protocols_config
        self.protocols = {}
        self.logger: logging.Logger = logger

        self._main_thread: threading.Thread = threading.main_thread()

        self.register_protocol('tcp', TcpServer, TcpRouterProtocol)
        self.register_protocol('http', HttpServer, HttpRouter)

    def register_protocol(
        self,
        protocol_name: str,
        server_class: type[ServerProtocol],
        router_class: type[RouterProtocol]
    ):
        self.protocols[protocol_name] = Protocol(protocol_name, server_class, router_class)

    def start(self):
        def run_servers():
            event_loop = get_loop_factory()()
            asyncio.set_event_loop(event_loop)
            tasks = set()
            for address in self.addresses:
                server = server_factory(address, self.protocols, self.routers, self.protocols_config, self.logger)
                tasks.add(event_loop.create_task(server.listen()))
            try:
                event_loop.run_forever()
            finally:
                for task in tasks:
                    task.cancel()
                event_loop.run_until_complete(event_loop.shutdown_asyncgens())
                event_loop.close()
                raise

        self._main_thread = threading.Thread(target=run_servers, daemon=True)
        self._main_thread.start()

    def join(self):
        self._main_thread.join()

    def print_servers(self):
        for address in self.addresses:
            print('  - ',repr(address.__class__))
            print(
                _('{protocol} server on {transport_protocol}:{port} is available at:').format(
                    protocol = address.protocol.upper(),
                    transport_protocol = address.transport_protocol,
                    port = address.port,
                )
            )
            print(*[f'  - {url}' for url in repr(address).split()], sep='\n')
