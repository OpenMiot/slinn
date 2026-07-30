from __future__ import annotations
from typing import Optional
from . import WebSocketConnection, TCPResponseChunk, FTDispatcher, SocketWrapper, utils
import urllib.parse
import socket


class Request:
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
        header: str,
        client_address: tuple[str, int],
        connection: SocketWrapper,
        server: 'Server',
        htrf: Optional[FTDispatcher] = None
    ):
        parse_header = lambda text: {
            pair.strip().split('=')[0]: '='.join(pair.split('=')[1:])
            for pair in text.split(',')[1:]
        }

        self.type = header.split('\r\n')[0].strip().split(' ')
        self.header = {
            'method': self.type[0],
            'link': ' '.join(self.type[1:-1]),
            'ver': self.type[-1],
            'data': self.parse_http_header(header)
        }
        self.payload = b''
        self.files = []
        self.ip, self.port = client_address[:2]
        self.protocol = self.header['ver'].split('/')[0]
        self.method = self.header['method']
        self.version = self.header['ver']
        self.full_link = urllib.parse.unquote_plus(self.header['link'])
        self.headers = self.header['data']
        host = self.headers.get('Host', '').split(':')
        if len(host) == 0:
            self.host = ''
        elif len(host) == 1:
            self.host = host[0].encode('ascii').decode('idna')
        elif len(host) > 1:
            self.host = ':'.join(host[:-1]).encode('ascii').decode('idna') + ':' + host[-1]
        self.user_agent = self.headers['User-Agent'] if 'User-Agent' in self.headers.keys() else \
            self.headers.get('user-agent', '')
        self.accept = self.headers.get('Accept', '').split(',')
        self.encoding = self.headers.get('Accept-Encoding', '').split(',')
        self.language = self.headers.get('Accept-Language', '').split(',')
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

        self.__str__ = self.__repr__

        self.connection = connection
        self.server = server
        self.htrf = htrf or server.htrf or FTDispatcher()
        self.body = RequestBody(self)

    def __repr__(self) -> str:
        return f'[{self.method}] request {self.full_link} from {"" if "." in self.ip else "["}{self.ip}{"" if "." in self.ip else "]"}:{self.port} on {self.host}'

    def respond(
        self,
        response_class: type[TCPResponseChunk],
        *args,
        **kwargs
    ) -> None:
        kwargs['request'] = self
        made = utils.optional(response_class(*args, **kwargs).make, version=self.version, htrf=self.htrf)
        if made is None:
            return
        self.connection.send(made)

    def recv(self, n_bytes: int) -> bytes:
        return self.connection.recv(n_bytes)

    def WebSocket(self, timeout: float) -> WebSocketConnection:
        conn = WebSocketConnection(self)
        conn.handshake()
        conn.settimeout(timeout)
        return conn


class RequestBody:
    def __init__(self, request: Request):
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

    def recv(self, n_bytes: int) -> bytes:
        if self.end():
            self._pending = False
            return b''
        try:
            data = self._request.recv(n_bytes)
            if len(data) + self._received >= self.size():
                return data[:self.size() - self._received]
            return data
        except (TimeoutError, socket.timeout):
            self._pending = False
            return b''

    def receive(self) -> bytes:
        return self.recv(min(self._request.server.max_bytes_per_receive, self.until_end()))

    def getline(self) -> bytes:
        line = bytearray()
        while b := self.receive():
            if b'\r\n' in b:
                lines = b.split(b'\r\n')
                line += lines[0]
                self._request.connection.paste(b[len(lines[0]) + 2:])
                break
            line += b
        return line

    def get(self) -> bytes:
        data = bytearray()
        while b := self.receive():
            data += b
        self._received = len(data)
        return bytes(data)

    def form(self) -> dict:
        if self._request.content_type[0] == 'application/x-www-form-urlencoded':
            return {
                key: urllib.parse.unquote_plus(val)
                for key, val in Request.get_args((self.getline()).decode()).items()
            }
        return {}

    def skip(self) -> None:
        while not self.end():
            self.receive()

    def files_boundary(self) -> Optional[str]:
        return self._request.content_type[1].get('boundary', None)

    def next_file_header(self) -> dict:
        while line := self.getline():
            if line == b'--' + self.files_boundary().encode():
                break
        header = []
        while line := self.getline():
            header.append(line)
        return Request.parse_http_header(b'\r\n'.join(header).decode())

    def next_file_body(self) -> bytes:
        data = bytearray()
        while line := self.getline():
            if line == b'--' + self.files_boundary().encode():
                self._request.connection.paste(b'--' + self.files_boundary().encode() + b'\r\n')
                break
            if line == b'--' + self.files_boundary().encode() + b'--':
                self._pending = False
                break
            data += line
        return bytes(data)
