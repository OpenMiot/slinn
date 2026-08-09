from typing import Protocol, Callable, Optional
from slinn.net import FilterProtocol


class RouterProtocol(Protocol):
    def __call__(self, request_filter: Optional[FilterProtocol] = None) ->  Callable[[Callable], Callable]: ...

    def check(self, *args, **kwargs) -> bool: ...
