from slinn.net.http.responses.http_response import HttpResponse, HttpHeadersMixin, HttpBodyMixin
from slinn.net.http import HttpHeaders, FTRouter, HttpRequest
from slinn import utils


class HttpRender(HttpResponse):
    
    """
    Renders any file to HttpResponse-based object
    """

    def __init__(
        self,
        file_path: str,
        headers: HttpHeaders = None,
        status: str = '200 OK',
        ppdata: dict | None = None,
        storage = open,
    ):
        self.file_path = file_path
        self.ppdata = ppdata or {}
        self.storage = storage
        
        async def render_hook(
            self,
            *,
            request: HttpRequest,
            ft_router: FTRouter | None = None,
            **kwargs
        ) -> dict:
            ft_router = ft_router or FTRouter()
            
            endpoint = None
            for _endpoint in ft_router.endpoints:
                if _endpoint.filter.check(request = request):
                    endpoint = _endpoint
                    break
            if not ft_router.endpoints or not endpoint:
                with self.storage(self.file_path, 'rb') as file:
                    self.payload = file.read()
                    return kwargs | {'request': request, 'ft_router': ft_router}
            with self.storage(self.file_path, 'rb') as file:
                response = await utils.optional(
                    endpoint.function,
                    file = file,
                    headers = self.headers,
                    ppdata = self.ppdata
                )
                self.headers.merge(response.headers)
                self.payload = await utils.optional(
                    response.make,
                    HttpBodyMixin,
                    chunked = False
                )
                return kwargs | {'request': request, 'ft_router': ft_router}
        
        super().__init__(self, None, headers, status, hooks={
            render_hook: (HttpHeadersMixin,)
        })
