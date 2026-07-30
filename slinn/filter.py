from __future__ import annotations
from . import utils


class Filter:

    """
    Base class for filtering requests
    """
    
    def __init__(self, _filter: str, methods: tuple = ('GET', 'POST')) -> None:
        self.filter = _filter
        self.methods = methods

    def check(self, request: 'Request') -> bool:
        return utils.rematcheswith(request.link, self.filter) and request.method.upper() in self.methods

    def size(self, request: 'Request') -> int:
        a = utils.min_restartswith_size(request.link, self.filter) if self.check(request) else 2147483647
        b = utils.Bmin_restartswith_size(request.link, self.filter) if self.check(request) else 2147483647
        if not self.check(request):
            return -1
        elif a == 2147483647:
            return 0
        else:
            return b

    def args(self, *args, **kwargs) -> dict:
        return {}
