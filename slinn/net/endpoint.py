from __future__ import annotations
from slinn.net import FilterProtocol
from collections.abc import Callable, Iterable
from functools import reduce
import inspect


class Endpoint:
    def __init__(
        self,
        _filter: FilterProtocol | None,
        handler: Callable,
        args: Callable[..., dict] = lambda *args, **kwargs: {}
    ):
        self.filter = _filter
        self.handler = handler
        self.args = args
        self.is_generator = inspect.isasyncgenfunction(handler)
    
    def apply_decorators(self, decorators: Iterable[Callable]) -> Endpoint:
        return Endpoint(self.filter, reduce(lambda res, func: func(res), decorators, self.handler), self.args)
