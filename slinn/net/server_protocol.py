from typing import Protocol, Any, Optional, Iterable
from slinn.net import RouterProtocol, PipeProtocol
from slinn.net.address import Address
import logging
import ssl


class ServerProtocol[TRouterProtocol: RouterProtocol](Protocol):
    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, dict[str, Any]],
        routers: Iterable[TRouterProtocol],
        logger: logging.Logger,
        ssl_context: Optional[ssl.SSLContext]
    ): ...

    async def reload(self, *routers: TRouterProtocol) -> None: ...

    async def listen(self) -> None: ...

    async def handle_pipe(
        self,
        pipe: PipeProtocol,
        client_address: Address,
        args: dict[Any, Any]
    ) -> None: ...

    async def shutdown(self) -> None: ...
