"""Import slinn`s modules"""
from . import Dispatcher, Path, Handle


class ApiDispatcher(Dispatcher):
    """FastAPI-style dispatcher for CRUD methods"""
    def __init__(self, *hosts, prefix: str=''):
        super().__init__(*hosts)
        self.prefix = prefix

    def get(self, path: str = '/'):
        """HTTP-GET Requests handler creator"""
        def decorator(func):
            _path = Path(self.prefix+path, ('GET',))
            self.handles.append(Handle(_path, func, _path.args))
            return func
        return decorator

    def post(self, path: str = '/'):
        """HTTP-POST Requests handler creator"""
        def decorator(func):
            _path = Path(self.prefix + path, ('POST',))
            self.handles.append(Handle(_path, func, _path.args))
            return func
        return decorator

    def patch(self, path: str = '/'):
        """HTTP-PATCH Requests handler creator"""
        def decorator(func):
            _path = Path(self.prefix + path, ('PATCH',))
            self.handles.append(Handle(_path, func, _path.args))
            return func
        return decorator

    def put(self, path: str = '/'):
        """HTTP-PUT Requests handler creator"""
        def decorator(func):
            _path = Path(self.prefix + path, ('PUT',))
            self.handles.append(Handle(_path, func, _path.args))
            return func
        return decorator

    def delete(self, path: str = '/'):
        """HTTP-DELETE Requests handler creator"""
        def decorator(func):
            _path = Path(self.prefix + path, ('DELETE',))
            self.handles.append(Handle(_path, func, _path.args))
            return func
        return decorator
