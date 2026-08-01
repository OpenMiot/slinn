from typing import Protocol, Optional, Any
from socket import AddressFamily, SocketKind
from asyncio import AbstractEventLoop
import ssl


class PipeProtocol(Protocol):
    def __init__(
        self,
        loop: AbstractEventLoop,
        *,
        family: AddressFamily | int = -1,
        type: SocketKind | int = -1,
        proto: int = -1,
        fileno: Optional[int] = None,
        timeout: float,
        ssl_context: Optional[ssl.SSLContext] = None
    ): ...

    def paste(self, data: Any) -> None: ...

    def set_timeout(self, timeout: float) -> None: ...

    def set_blocking(self, blocking: bool) -> None: ...

    def get_sock_opt(self, *args) -> int | bytes: ...

    def file_no(self) -> int: ...

    def close(self) -> None: ...

    @property
    def closed(self) -> bool: ...
