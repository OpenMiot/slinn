from slinn.net.http.responses.http_response import HttpResponse
from slinn.net.http import HttpRequest
from slinn import utils, FTDispatcher
from typing import Optional


class HttpRender(HttpResponse):
    
    """
    Renders any file to HttpResponse-based object
    """

    def __init__(
        self,
        file_path: str,
        data: Optional[list[tuple]] = None,
        status: str = '200 OK',
        ppdata: Optional[dict] = None,
        storage = open,
        request: Optional[HttpRequest] = None
    ):
        self.file_path = file_path
        self.data = data if data is not None else []
        self.status = status
        self.ppdata = ppdata if ppdata is not None else {}
        self.storage = storage

    def make(
        self,
        request: HttpRequest,
        htrf: Optional[FTDispatcher] = None
    ) -> bytes:
        def size(_filter: str, text: str) -> int:
            a = utils.min_restartswith_size(text, _filter) if utils.rematcheswith(text, _filter) else 2147483647
            b = utils.Bmin_restartswith_size(text, _filter) if utils.rematcheswith(text, _filter) else 2147483647
            if not utils.rematcheswith(text, _filter):
                return -1
            if a == 2147483647:
                return 0
            return b
        htrf = htrf or FTDispatcher()
        if htrf.handles == []:
            with self.storage(self.file_path, 'rb') as file:
                return HttpResponse(file.read(), data=self.data).make(request = request)
        
        sizes = [size(handle.filter, self.file_path) for handle in htrf.handles]
        handle = htrf.handles[sizes.index(max(sizes))]
        with self.storage(self.file_path, 'rb') as file:
            return utils.optional(utils.optional(handle.function, file=file, data=self.data, ppdata=self.ppdata).make, version=version, htrf=htrf)
