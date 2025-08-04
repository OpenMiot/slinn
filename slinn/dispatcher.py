from __future__ import annotations
from . import Handle, Filter, LinkFilter


class Dispatcher:

    """
    Class for handling requests
    """
    
    def __init__(self, *hosts: tuple) -> None:
        self.handles = []
        self.hosts = hosts if hosts != () else ('.*', )

    def __call__(self, _filter: Filter) -> callable:
        def wrapper(func):
            self.handles.append(Handle(_filter, func, _filter.args))
            return func

        return wrapper

    def static(self, link: str, http_response, *args, **kwargs) -> Dispatcher:
        async def handler():
            return http_response(*args, **kwargs)
        self.handles.append(Handle(LinkFilter(link), handler))
        return self
