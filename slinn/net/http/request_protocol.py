from typing import Protocol, Any
from asyncio import AbstractEventLoop
from slinn.net import PipeProtocol
from slinn import Address


class RequestProtocol(Protocol):
    def __init__(
        self,
        loop: AbstractEventLoop,
        address: Address,
        pipe: PipeProtocol,
        data: dict[Any, Any]
    ): ...
