"""Import slinn`s modules"""
from . import Dispatcher, Path, Handle
import functools


class ApiDispatcher(Dispatcher):
    """FastAPI-style dispatcher for CRUD methods"""
    def __init__(self, *hosts, prefix: str=''):
        super().__init__(*hosts)
        self.prefix = prefix

        self.get = functools.partial(self._register_handler_decorator, methods=('GET', ))
        self.post = functools.partial(self._register_handler_decorator, methods=('POST',))
        self.patch = functools.partial(self._register_handler_decorator, methods=('PATH',))
        self.put = functools.partial(self._register_handler_decorator, methods=('GET',))
        self.delete = functools.partial(self._register_handler_decorator, methods=('GET',))
        self.options = functools.partial(self._register_handler_decorator, methods=('GET',))

    def _register_handler_decorator(self, path: str = '/', methods: tuple[str] = ()):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            _path = Path(self.prefix + path, methods)
            self.handles.append(Handle(_path, func, _path.args))
            return wrapper

        return decorator
