from typing import Protocol, Callable
from slinn.net import FilterProtocol


class RouterProtocol(Protocol):
    def __call__(self, request_filter: FilterProtocol) ->  Callable[[Callable], Callable]: ...

    def check(self, *args, **kwargs) -> bool: ...
