from __future__ import annotations
from slinn.net.http import HttpHeaders
import re


rematcheswith = lambda text, reg: re.match('^' + reg + '$', text) is not None

class Filter:

    """
    Base class for filtering requests
    """
    
    def __init__(self, _filter: str, methods: tuple = ('GET', )) -> None:
        self.filter = re.compile(_filter)
        self.methods = methods

    def check(self, recv_headers: HttpHeaders, *, skip_methods_check: bool = False, **kwargs) -> bool:
        link = recv_headers.path[:(recv_headers.path.index('?') if '?' in recv_headers.path else None)]
        return (recv_headers.method in self.methods or skip_methods_check) and self.filter.match(link)

    def args(self, *args, **kwargs) -> dict:
        return {}
