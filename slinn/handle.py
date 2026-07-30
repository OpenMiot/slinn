from __future__ import annotations
from typing import Callable


class Handle:
    def __init__(self, _filter: 'Filter', function: Callable, args: Callable[..., dict] = lambda *args, **kwargs: {}):
        self.filter = _filter
        self.function = function
        self.args = args
