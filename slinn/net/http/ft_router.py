from slinn.net import Endpoint
from slinn.net.http.filters import Filter
from typing import Callable


class FTRouter:

    """
    Class for handling filetypes
    """
    
    def __init__(self) -> None:
        self.endpoints = []

    def by_extension(self, extension: str) -> Callable[[Callable], Callable]:
        def wrapper(func):
            self.endpoints.append(Endpoint(Filter(r'.*\.' + extension + r'$'), func))
            return func
        return wrapper
    
    def by_regexp(self, regexp: str) -> Callable[[Callable], Callable]:
        def wrapper(func):
            self.endpoints.append(Endpoint(regexp, func))
            return func
        return wrapper
