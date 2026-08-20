from __future__ import annotations
from slinn.net import FilterProtocol
from collections.abc import Callable, Iterable
from functools import reduce
import inspect


class Endpoint:
    def __init__(
        self,
        _filter: FilterProtocol | None,
        function: Callable,
        args: Callable[..., dict] = lambda *args, **kwargs: {}
    ):
        self.filter = _filter
        self.function = function
        self.args = args
        self.is_generator = inspect.isasyncgenfunction(function)
    
    def apply_decorators(self, decorators: Iterable[Callable]) -> Endpoint:
        return Endpoint(self.filter, reduce(lambda res, func: func(res), decorators, self.function), self.args)
