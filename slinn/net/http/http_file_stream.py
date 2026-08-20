from slinn.net.http import HttpHeaders, HttpResponder, HttpRequest
from slinn.net.http.responses import HttpResponse, HttpHeadersMixin, HttpBodyMixin
from slinn.net.tcp import TcpPipe
from slinn.net import Endpoint
from slinn import utils
from collections.abc import AsyncGenerator
import enum


class ContentDisposition(enum.Enum):
    ATTACHMENT = 'attachment'
    INLINE = 'inline'


class HttpFileStream:
    def __init__(
        self,
        request: HttpRequest,
        client_pipe: TcpPipe,
        file,
        filename: str,
        content_type: str,
        total: int,
        content_disposition: ContentDisposition = ContentDisposition.INLINE,
        chunk_size: int = 256*1024,
    ):
        self.range = 'Range' in request.headers
        if self.range:
            http_range = (0, chunk_size - 1)
            if request.headers.get('Range', '').startswith('bytes='):
                http_range = request.headers['Range'].removeprefix('bytes=').split(',')[0].strip().split('-')
            self.range_from = int(http_range[0]) if http_range[0] else 0
            self.range_to = int(http_range[1]) if http_range[1] else self.range_from + chunk_size - 1
        self.request = request
        self.client_pipe = client_pipe
        self._file = file
        self.filename = filename
        self.content_type = content_type
        self.total = total
        self.content_disposition = content_disposition
        self.chunk_size = chunk_size
    
    async def file_range(self) -> AsyncGenerator:
        chunk_size = min(self.chunk_size, self.range_to - self.range_from + 1)
        yield HttpResponse(
            HttpHeaders(default_headers = {
                'Content-Disposition': (f'{self.content_disposition.value}; filename="{self.filename}"', ),
                'Content-Range': (f'bytes {self.range_from}-{self.range_from+chunk_size-1}/{self.total}', ),
                'Accept-Ranges': ('bytes', )
            }),
            status = '206 Partial Content',
            content_type = self.content_type,
            body_mixin = False
        )
        self._file.seek(self.range_from)
        yield self._file.read(chunk_size)
    
    async def file_full(self) -> AsyncGenerator:
        yield HttpResponse(
            headers = HttpHeaders(default_headers = {
                'Content-Disposition': (f'{self.content_disposition.value}; filename="{self.filename}"', ),
                'Accept-Ranges': ('bytes', ),
                'Content-Length': (self.total, )
            }),
            content_type = self.content_type,
            body_mixin = False
        )
        while True:
            chunk = self._file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    async def file(self) -> AsyncGenerator:
        async for chunk in self.file_range() if self.range else self.file_full():
            yield chunk
