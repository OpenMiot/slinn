from typing import Any
from slinn.net.tcp import TcpServer
from slinn.net.http import HttpRouter, HCRouter, FTRouter, HttpRequestBus, HttpProtocolBus
from slinn.net.address import Address
from slinn.net import ServerProtocol
lazy from slinn.api import ProjectApi
from slinn.tools.manage.misc import load_module
from collections.abc import Iterable
import logging
import ssl
import os


class HttpServer(ServerProtocol):
    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, dict[str, Any]],
        logger: logging.Logger,
        buses: Iterable[HttpRequestBus] | None = None,
        ssl_context: ssl.SSLContext | None = None
    ) -> None:
        self.address = address
        self.protocols_config = protocols_config
        self.logger = logger
        self.http_request_buses = buses
        self.ssl_context = ssl_context
    
        self.http_config = self.protocols_config.get('http', {})

        self._max_requests = self.http_config['max_requests']
        self._max_header_size = self.http_config['max_header_size']
        
        self.project = ProjectApi(os.getcwd())

    async def reload(self, *routers: HttpRouter) -> None:
        self.routers = routers
        await self._server.reload()

    async def listen(self):
        await self.project.load_config()
        self.routers = [*app.load_http_routers() async for app in self.project.load_apps()]
        
        self._http_codes_router = HCRouter()
        if 'http_codes_router' in self.http_config:
            *mod, obj =  self.http_config['http_codes_router'].split('.')
            self._http_codes_router = getattr(load_module('/'.join(mod)+'.py'), obj)

        self._file_types_router = FTRouter()
        if 'file_types_router' in self.http_config:
            *mod, obj =  self.http_config['file_types_router'].split('.')
            self._file_types_router = getattr(load_module('/'.join(mod)+'.py'), obj)
        
        self.buses = list(self.http_request_buses or (HttpProtocolBus(
            max_requests = self._max_requests,
            routers = self.routers,
            file_types_router = self._file_types_router,
            http_codes_router = self._http_codes_router,
            logger = self.logger
        ), ))
        
        self._server = TcpServer(
            address = self.address,
            protocols_config = self.protocols_config,
            logger = self.logger,
            buses = self.buses,
            ssl_context = self.ssl_context,
        )
        
        self.handle_pipe = self._server.handle_pipe
        self.shutdown = self._server.shutdown
        
        await self._server.listen()
