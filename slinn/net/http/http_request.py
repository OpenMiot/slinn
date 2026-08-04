from __future__ import annotations
from slinn import FTDispatcher
from slinn.net.tcp import TcpPipe
from slinn.net.address import Address
from slinn.utils import lazy_import
from typing import Optional
import urllib.parse
import socket
import asyncio


class HttpRequest:
    """
    Representation of HTTP request from client
    """

    parse_http_header = staticmethod(lambda http_header: {
        line.split(':')[0].strip(): ':'.join(line.split(':')[1:]).strip()
        for line in http_header.split('\r\n')
    })
    get_args = staticmethod(lambda text: {
        pair.split('=')[0]: '='.join(pair.split('=')[1:])
        for pair in text.split('&')
    })

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        header: str,
        client_address: Address,
        client_pipe: TcpPipe,
        server: 'Server',
        htrf: Optional[FTDispatcher] = None,
    ):
        parse_header = lambda text: {
            pair.strip().split('=')[0]: '='.join(pair.split('=')[1:])
            for pair in text.split(',')[1:]
        }

        self.type = header.split('\r\n')[0].strip().split(' ')
        self.ip, self.port = client_address.host, client_address.port
        self.protocol = self.type[-1].split('/')[0]
        self.method = self.type[0]
        self.version = self.type[-1]
        self.full_link = urllib.parse.unquote_plus(' '.join(self.type[1:-1]))
        self.headers = self.parse_http_header(header)
        host = self.headers.get('Host', '').split(':')
        match len(host):
            case 0:
                self.host = ''
            case 1:
                self.host = host[0].encode('ascii').decode('idna')
            case _:
                self.host = ':'.join(host[:-1]).encode('ascii').decode('idna') + ':' + host[-1]
        self.user_agent = self.headers['User-Agent'] if 'User-Agent' in self.headers.keys() else \
            self.headers.get('user-agent', '')
        self.accept = self.headers.get('Accept', '').split(',')
        self.accept_encoding = self.headers.get('Accept-Encoding', '').split(',')
        self.accept_language = self.headers.get('Accept-Language', '').split(',')
        self.link = self.full_link[:(self.full_link.index('?') if '?' in self.full_link else None)]
        self.args = self.get_args(
            self.full_link[(self.full_link.index('?') + 1 if '?' in self.full_link else len(self.full_link)):])
        self.cookies = {c.split('=')[0].strip(): c.split('=')[1] for c in
                        self.headers['Cookie'].split(';')} if 'Cookie' in self.headers else dict()
        self.content_length = int(self.headers.get('Content-Length', '0'))
        self.content_type = self.headers.get('Content-Type', self.headers.get('content-type', '')).split(';')[0], dict([
            tuple(arg.strip().split('='))
            for arg in self.headers.get('Content-Type', self.headers.get('content-type', '')).split(';')[1:]
        ])
        self.keep_alive = parse_header(self.headers.get('Keep-Alive', ''))
        self.connection = self.headers.get('Connection', 'close' if self.version == 'HTTP/1.0' else 'Keep-Alive')

        self.__str__ = self.__repr__

        self.client_pipe = client_pipe
        self.server = server
        self.loop = loop
        self.body = RequestBody(self)

    def __repr__(self) -> str:
        return f'[{self.method}] request {self.full_link} from {"" if "." in self.ip else "["}{self.ip}{"" if "." in self.ip else "]"}:{self.port} on {self.host}'

    async def recv(self, n_bytes: int) -> bytes:
        return await self.connection.recv(n_bytes)

    async def WebSocket(self, timeout: float) -> 'WebSocketConnection':
        from slinn.net.ws import WebSocketConnection

        conn = WebSocketConnection(self)
        await conn.handshake()
        conn.settimeout(timeout)
        return conn


class RequestBody:
    _request: HttpRequest

    def __init__(self, request: HttpRequest):
        self._request = request
        self._received = 0
        self._pending = True

    def size(self) -> int:
        return self._request.content_length

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
            data = await self._request.recv(n_bytes)
            if len(data) + self._received >= self.size():
                return data[:self.size() - self._received]
            return data
        except (TimeoutError, socket.timeout):
            self._pending = False
            return b''

    async def receive(self) -> bytes:
        return await self.recv(min(self._request.server.max_bytes_per_receive, self.until_end()))

    async def getline(self) -> bytes:
        line = bytearray()
        while b := await self.receive():
            if b'\r\n' in b:
                lines = b.split(b'\r\n', 1)
                line += lines[0]
                self._request.connection.paste(b[len(lines[0]) + 2:])
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
        if self._request.content_type[0] == 'application/x-www-form-urlencoded':
            return {
                key: urllib.parse.unquote_plus(val)
                for key, val in HttpRequest.get_args((await self.getline()).decode()).items()
            }
        return {}

    async def skip(self):
        while not self.end():
            await self.receive()

    def files_boundary(self) -> Optional[str]:
        return self._request.content_type[1].get('boundary', None)

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
                self._request.connection.paste(b'--' + self.files_boundary().encode() + b'\r\n')
                break
            if line == b'--' + self.files_boundary().encode() + b'--':
                self._pending = False
                break
            data += line + b'\r\n'
        return bytes(data)
