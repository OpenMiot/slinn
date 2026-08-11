from typing import Protocol, Callable, Optional
from slinn.net import FilterProtocol


class RouterProtocol[TFilterProtocol: FilterProtocol](Protocol):
    def __call__(self, request_filter: TFilterProtocol) ->  Callable[[Callable], Callable]: ...

    def check(self, *args, **kwargs) -> bool: ...
