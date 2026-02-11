from __future__ import annotations

import functools

from . import Handle, Filter, Path, utils


class Dispatcher:

    """
    Class for handling requests 
    """
    
    def __init__(self, *hosts: str) -> None:
        self.handles = []
        self.hosts = hosts if hosts != () else ('.*', )
        self.hosts = [host for host in hosts]

    def __call__(self, _filter: Filter) -> callable:
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            self.handles.append(Handle(_filter, wrapper, _filter.args))
            return wrapper

        return decorator

    def check(self, host):
        return len(self.hosts) == 0 or True in [utils.restartswith(host, _host) for _host in self.hosts]

    def static(self, link: str, http_response, *args, **kwargs) -> Dispatcher:
        async def handler():
            return http_response(*args, **kwargs)
        _path = Path(link)
        self.handles.append(Handle(_path, handler, _path.args))
        return self

    def sstatic(self, link: str, http_response, *args, **kwargs) -> Dispatcher:
        def handler():
            return http_response(*args, **kwargs)
        _path = Path(link)
        self.handles.append(Handle(_path, handler, _path.args))
        return self

