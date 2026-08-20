from __future__ import annotations
from slinn import utils
from slinn.net.http import HttpRequest
import re


rematcheswith = lambda text, reg: re.match('^' + reg + '$', text) is not None

class Filter:

    """
    Base class for filtering requests
    """
    
    def __init__(self, _filter: str, methods: tuple = ('GET', )) -> None:
        self.filter = re.compile(_filter)
        self.methods = methods

    def check(self, request: HttpRequest, **kwargs) -> bool:
        link = request.headers.path[:(request.headers.path.index('?') if '?' in request.headers.path else None)]
        return request.headers.method in self.methods and self.filter.match(link)

    def args(self, *args, **kwargs) -> dict:
        return {}
