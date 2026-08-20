from collections.abc import Callable
from typing import Protocol


class MiddlewareProtocol(Protocol):
    def __init__(self, *args, **kwargs): ...
    
    def __call__(self, func: Callable) -> Callable: ...
