from __future__ import annotations
from typing import Callable, Optional
from slinn.net import FilterProtocol
import inspect


class Endpoint:
    def __init__(
        self,
        _filter: Optional[FilterProtocol],
        function: Callable,
        args: Callable[..., dict] = lambda *args, **kwargs: {}
    ):
        self.filter = _filter
        self.function = function
        self.args = args
        self.is_generator = inspect.isasyncgenfunction(function)
