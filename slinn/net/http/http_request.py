from __future__ import annotations
from slinn import FTDispatcher, _
from slinn.net.tcp import TcpPipe
from slinn.net.http import HttpHeaders, HttpVersion
from slinn.net.address import Address
import urllib.parse
import asyncio


get_args = lambda text: {
    pair.split('=')[0]: '='.join(pair.split('=')[1:])
    for pair in text.split('&')
}

parse_header = lambda text: {
    pair.strip().split('=')[0]: '='.join(pair.split('=')[1:])
    for pair in text.split(',')[1:]
}

class HttpRequest:
    __slots__ = (
        'accept', 'accept_encoding', 'accept_language', 'args', 'body', 'client_pipe', 'connection', 'content_length',
        'content_type', 'cookies', 'headers', 'host', 'ip', 'keep_alive', 'link', 'loop', 'method', 'path', 'port',
        'protocol', 'server', 'type', 'user_agent', 'version',
    )

    """ 
    Representation of HTTP request from client
    """

    

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        header: str,
        client_addr: Address,
        client_pipe: TcpPipe,
        server: 'Server',
    ):
        

        self.ip, self.port = client_addr.host, client_addr.port
        self.headers = HttpHeaders.parse(header.encode())
        self.method = self.headers.method
        self.version = self.headers.version
        self.path = self.headers.path
        host = self.headers.authority.split(':')
        match len(host):
            case 0:
                self.host = ''
            case 1:
                self.host = host[0].encode('ascii').decode('idna')
            case _:
                self.host = ':'.join(host[:-1]).encode('ascii').decode('idna') + ':' + host[-1]
        self.user_agent = self.headers.get('User-Agent')
        self.accept = self.headers.get('Accept', '').split(',')
        self.accept_encoding = self.headers.get('Accept-Encoding', '').split(',')
        self.accept_language = self.headers.get('Accept-Language', '').split(',')
        self.link = self.path[:(self.path.index('?') if '?' in self.path else None)]
        self.args = self.get_args(
            self.path[(self.path.index('?') + 1 if '?' in self.path else len(self.path)):])
        self.cookies = {c.split('=')[0].strip(): c.split('=')[1] for c in
                        self.headers.get('Cookie').split(';')} if 'Cookie' in self.headers else dict()
        self.content_length = int(self.headers.get('Content-Length', '0'))
        self.content_type = self.headers.get('Content-Type', self.headers.get('content-type', '')).split(';')[0], dict([
            tuple(arg.strip().split('='))
            for arg in self.headers.get('Content-Type', self.headers.get('content-type', '')).split(';')[1:]
        ])
        self.keep_alive = parse_header(self.headers.get('Keep-Alive', ''))
        self.connection = self.headers.get('Connection', 'close' if self.version == 'HTTP/1.0' else 'Keep-Alive')

        self.client_pipe = client_pipe
        self.server = server
        self.loop = loop
        self.body = HttpRequestBody(self)

    def __str__(self) -> str:
        return _('[{method}] request {link} from {client_addr} on {authority}').format(
            method = self.method,
            link = self.path,
            client_addr = ('' if '.' in self.ip else '[') +
                          (self.ip) +
                          ('' if '.' in self.ip else ']') +
                          ':' +
                          (self.port),
            authority = self.host
        )

    async def get_websocket(self, timeout: float) -> 'WebSocketConnection':
        from slinn.net.ws import WebSocketConnection

        conn = WebSocketConnection(self)
        await conn.handshake()
        conn.set_timeout(timeout)
        return conn


class HttpRequestBody:
    def __init__(self, headers: HttpHeaders, client_pipe: TcpPipe):
        self._headers: HttpHeaders = headers
        self._client_pipe: TcpPipe = client_pipe
        self._received: int = 0
        self._pending: bool = True

    def size(self) -> int:
        return int(self._headers.get('Content-Length', '0'))

    def end(self) -> bool:
        return self.until_end() <= 0

    def until_end(self) -> int:
        if not self._pending:
            return 0
        return self.size() - self._received

    async def recv(self, n_bytes: int) -> bytes:
        if self.end():
            self._pending = False
            return b''
        try:
            data = await self._client_pipe.recv(n_bytes)
            if len(data) + self._received >= self.size():
                return data[:self.size() - self._received]
            return data
        except TimeoutError:
            self._pending = False
            return b''

    async def receive(self) -> bytes:
        return await self.recv(self.until_end())

    async def getline(self) -> bytes:
        line = bytearray()
        while b := await self.receive():
            if b'\r\n' in b:
                lines = b.split(b'\r\n', 1)
                line += lines[0]
                self._client_pipe.connection.paste(b[len(lines[0]) + 2:])
                break
            line += b
        return line

    async def get(self) -> bytes:
        data = bytearray()
        while b := await self.receive():
            data += b
        self._received = len(data)
        return bytes(data)

    async def form(self) -> dict:
        if self._headers.get('Content-Type').split(';')[0] == 'application/x-www-form-urlencoded':
            return {
                key: urllib.parse.unquote_plus(val)
                for key, val in HttpRequest.get_args((await self.getline()).decode()).items()
            }
        return {}

    async def skip(self):
        while not self.end():
            await self.receive()

    def files_boundary(self) -> str | None:
        _content_type = self._headers.get('Content-Type')
        return dict([
            tuple(arg.strip().split('='))
            for arg in _content_type.split(';')[1:]
        ]).get('boundary')

    async def next_file_header(self) -> dict:
        while line := await self.getline():
            if line == b'--' + self.files_boundary().encode():
                break
        header = []
        while line := await self.getline():
            header.append(line)
        return HttpRequest.parse_http_header(b'\r\n'.join(header).decode())

    async def next_file_body(self) -> bytes:
        data = bytearray()
        while line := await self.getline():
            if line == b'--' + self.files_boundary().encode():
                self._client_pipe.connection.paste(b'--' + self.files_boundary().encode() + b'\r\n')
                break
            if line == b'--' + self.files_boundary().encode() + b'--':
                self._pending = False
                break
            data += line + b'\r\n'
        return bytes(data)
