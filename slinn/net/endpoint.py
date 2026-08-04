from __future__ import annotations
from typing import Callable
from slinn.net import FilterProtocol


class Endpoint:
    def __init__(
        self,
        _filter: FilterProtocol,
        function: Callable,
        args: Callable[..., dict] = lambda *args, **kwargs: {}
    ):
        self.filter = _filter
        self.function = function
        self.args = args
