from __future__ import annotations
from . import Handle, Filter, LinkFilter, Path


class Dispatcher:

    """
    Class for handling requests 
    """
    
    def __init__(self, *hosts: str) -> None:
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
        _path = Path(link)
        self.handles.append(Handle(_path, handler, _path.args))
        return self
