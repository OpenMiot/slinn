from typing import Protocol, Any, Optional
from slinn.net import RouterProtocol, RequestProtocol, PipeProtocol
from slinn import Address
import logging
import ssl


class ServerProtocol(Protocol):
    def __init__(
        self,
        address: Address,
        protocol_config: dict[str, Any],
        logger: logging.Logger,
        ssl_context: Optional[ssl.SSLContext]
    ): ...

    async def reload(self, *routers:  RouterProtocol) -> None: ...

    async def listen(self) -> None: ...

    async def handle_pipe(
        self,
        pipe: PipeProtocol,
        client_address: Address,
        data: dict[Any, Any]
    ) -> None: ...

    async def shutdown(self) -> None: ...
