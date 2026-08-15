from __future__ import annotations
from slinn import utils
from slinn.net.http import HttpHeaders


class Filter:

    """
    Base class for filtering requests
    """
    
    def __init__(self, _filter: str, methods: tuple = ('GET', 'POST')) -> None:
        self.filter = _filter
        self.methods = methods

    def check(self, headers: HttpHeaders) -> bool:
        link = headers.path[:(headers.path.index('?') if '?' in headers.path else None)]
        return utils.rematcheswith(link, self.filter) and headers.method in self.methods

    async def size(self, headers: HttpHeaders) -> int:
        link = headers.path[:(headers.path.index('?') if '?' in headers.path else None)]
        a = utils.min_restartswith_size(link, self.filter) if self.check(headers) else 2147483647
        b = utils.Bmin_restartswith_size(link, self.filter) if self.check(headers) else 2147483647
        if not self.check(headers):
            return -1
        elif a == 2147483647:
            return 0
        else:
            return b

    def args(self, *args, **kwargs) -> dict:
        return {}
