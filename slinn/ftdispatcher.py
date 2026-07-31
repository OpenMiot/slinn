from . import Endpoint
from typing import Callable


class FTDispatcher:

    """
    Class for handling filetypes
    """
    
    def __init__(self) -> None:
        self.handles = []

    def by_extension(self, extension: str) -> Callable[[Callable], Callable]:
        def wrapper(func):
            self.handles.append(Endpoint(r'.*\.' + extension + r'$', func))
            return func

        return wrapper
    
    def by_regexp(self, regexp: str) -> Callable[[Callable], Callable]:
        def wrapper(func):
            self.handles.append(Endpoint(regexp, func))
            return func

        return wrapper
