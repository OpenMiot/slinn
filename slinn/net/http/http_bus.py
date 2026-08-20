from slinn.net.http import HttpRequest, FTRouter, HCRouter, HttpResponder, HttpRouter, HttpHeaders
from slinn.net.http.events import HttpRequestReceived
from slinn.net.tcp import TcpPipe
from slinn.net.address import Address
from slinn.eda import BaseBus, on
from slinn.utils import optional
from collections.abc import Iterable
import asyncio


class HttpBus(BaseBus):
    def __init__(
        self,
        routers: Iterable[HttpRouter],
        file_types_router: FTRouter,
        http_codes_router: HCRouter
    ):
        self.routers = routers
        self.file_types_router = file_types_router
        self.http_codes_router = http_codes_router
        super().__init__()
    
    @on(HttpRequestReceived())
    async def on_request_received(
        self,
        request: HttpRequest,
        client_pipe: TcpPipe,
        client_address: Address,
        extend_headers: HttpHeaders
    ):
        loop = asyncio.get_running_loop()
        t3 = loop.time()
        responder = HttpResponder(client_pipe, self.file_types_router, self.http_codes_router)
        endpoints = []
        meta = {
            'client_pipe': client_pipe,
            'client_address': client_address,
            'request': request,
        }
        for router in self.routers:
            if router.check(**meta):
                endpoints.extend(router.endpoints)
        endpoint = None
        for _endpoint in endpoints:
            if _endpoint.filter.check(**meta):
                endpoint = _endpoint
                break
        if not endpoint:
            endpoint = self.http_codes_router[404]
        t4 = loop.time()
        await responder.handle_endpoint(
            endpoint = endpoint,
            request = request,
            args = meta,
            extend_headers = extend_headers.extend(HttpHeaders(default_headers = {
                'Server-Timing': ((
                    f'route;desc="Routing";dur={(t4-t3)*1000}'
                ), )
            })),
            skip_body = True,
            trail = True,
            may_close = True
        )
