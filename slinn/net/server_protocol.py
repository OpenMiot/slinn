from typing import Protocol, Any
from slinn.net import PipeProtocol
from slinn.net.address import Address
from slinn.eda import BaseBus
from collections.abc import Iterable
import logging
import ssl


class ServerProtocol[TBus: BaseBus](Protocol):
    def __init__(
        self,
        address: Address,
        protocols_config: dict[str, dict[str, Any]],
        logger: logging.Logger,
        bus: Iterable[TBus],
        ssl_context: ssl.SSLContext | None
    ): ...

    async def reload(self, *buses: TBus) -> None: ...

    async def listen(self) -> None: ...

    async def handle_pipe(
        self,
        pipe: PipeProtocol,
        client_address: Address,
        args: dict[Any, Any]
    ) -> None: ...

    async def shutdown(self) -> None: ...
