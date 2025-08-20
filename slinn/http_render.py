from slinn.http_response import HttpResponse
from slinn import utils, FTDispatcher


class HttpRender(HttpResponse):
    
    """
    Renders any file to HttpResponse-based object
    """

    def __init__(self, file_path: str, data: list[tuple] = None, status: str = '200 OK', ppdata: dict = None, storage = open) -> None:
        self.file_path = file_path
        self.data = data if data is not None else []
        self.status = status
        self.ppdata = ppdata if ppdata is not None else {}
        self.storage = storage

    def make(self, version: str = 'HTTP/2.0', use_gzip: bool = False, htrf: FTDispatcher = FTDispatcher()) -> bytes:
        def size(_filter: str, text: str) -> int:
            a = utils.min_restartswith_size(text, _filter) if utils.rematcheswith(text, _filter) else 2147483647
            b = utils.Bmin_restartswith_size(text, _filter) if utils.rematcheswith(text, _filter) else 2147483647
            if not utils.rematcheswith(text, _filter):
                return -1
            elif a == 2147483647:
                return 0
            else:
                return b
        if htrf.handles == []:
            print(self.file_path)
            with self.storage(self.file_path, 'rb') as file:
                return HttpResponse(file.read(), data=self.data).make(use_gzip=use_gzip)
        sizes = [size(handle.filter, self.file_path) for handle in htrf.handles]
        handle = htrf.handles[sizes.index(max(sizes))]
        with self.storage(self.file_path, 'rb') as file:
            return utils.optional(utils.optional(handle.function, file=file, data=self.data, ppdata=self.ppdata).make, version=version, use_gzip=use_gzip, htrf=htrf)
