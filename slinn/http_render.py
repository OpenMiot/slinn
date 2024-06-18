from slinn.http_response import HttpResponse
from slinn import utils, FTDispatcher


class HttpRender(HttpResponse):
    
    """
    Renders any file to HttpResponse-based object
    """

    def __init__(self, file_path: str, data: list[tuple] = None, status: str = '200 OK') -> None:
        self.file_path = file_path
        self.data = data
        self.status = status

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
            with open(self.file_path, 'rb') as file:
                return HttpResponse(file.read()).make(use_gzip=use_gzip)
        sizes = [size(handle.filter, self.file_path) for handle in htrf.handles]
        handle = htrf.handles[sizes.index(max(sizes))]
        with open(self.file_path, 'rb') as file:
            return utils.optional(utils.optional(handle.function, file=file).make, version=version, use_gzip=use_gzip, htrf=htrf)
