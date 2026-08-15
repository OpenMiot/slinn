from slinn.net.http import HttpRequest
from slinn.net.http.responses import HttpResponse, HttpHeaderResponse, HttpChunkResponse
from slinn import utils
import enum


class ContentDisposition(enum.Enum):
    ATTACHMENT = 'attachment'
    INLINE = 'inline'


class HttpFileStream:
    def __init__(
        self,
        request: HttpRequest,
        file, filename: str,
        content_type: str,
        total: int,
        content_disposition: ContentDisposition = ContentDisposition.INLINE,
        chunk_size: int = 256*1024,
    ):
        self.range = 'Range' in request.headers.keys()
        if self.range:
            http_range = (0, CHUNK_SIZE - 1)
            if request.headers.get('Range', '').startswith('bytes='):
                http_range = request.headers['Range'].removeprefix('bytes=').split(',')[0].strip().split('-')
            self.range_from = int(http_range[0]) if http_range[0] else 0
            self.range_to = int(http_range[1]) if http_range[1] else self.range_from + CHUNK_SIZE - 1
        self.request = request
        self.file = file
        self.filename = filename
        self.content_type = content_type
        self.total = total
        self.content_disposition = content_disposition
        self.chunk_size = chunk_size
    
    async def file_range(self) -> HttpResponse:
        self.file.seek(self.range_from)
        chunk = self.file.read(min(self.chunk_size, self.range_to - self.range_from + 1))
        return HttpResponse(
            data = [
                ('Content-Disposition', f'{self.content_disposition.value}; filename="{self.filename}"'),
                ('Content-Range', f'bytes {self.range_from}-{self.range_from+len(chunk)-1}/{self.total}'),
                ('Accept-Ranges', 'bytes')
            ],
            payload = chunk,
            status = '206 Partial Content',
            content_type = self.content_type
        )
    
    async def file_full(self):
        yield HttpHeaderResponse(
            data = [
                ('Content-Disposition', f'{self.content_disposition.value}; filename="{self.filename}"'),
                ('Accept-Ranges', 'bytes'),
                ('Content-Length', self.total)
            ],
            use_gzip = False,
            content_type = self.content_type
        )
        while True:
            chunk = self.file.read(self.chunk_size)
            yield HttpChunkResponse(chunk)
            if not chunk:
                break

    async def respond(self):
        async def respond_request(response):
            made = utils.optional(response.make, request = self.request)
            if made is None:
                return
            await self.request.client_pipe.send(made)
        if self.range:
            await respond_request(await self.file_range())
        else:
            async for value in self.file_full():
                await respond_request(value)
