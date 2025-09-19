from . import File, WebSocketConnection, FTDispatcher, utils
import urllib.parse
import socket


class Request:
    """
    Representation of HTTP request from client
    """

    @staticmethod
    def parse_http_header(http_header: str) -> dict:
        result = {}
        for line in http_header.split('\r\n'):
            key, value = line.split(':')[0], ':'.join(line.split(':')[1:])
            result[key.strip()] = value.strip()
        return result

    def __init__(self, header: str, client_address: tuple[str, int], connection, server, htrf: FTDispatcher = FTDispatcher()) -> None:
        def get_args(text):
            return {} if text == '' else {pair.split('=')[0]: '='.join(pair.split('=')[1:]) for pair in text.split('&')}

        self.type = header.split('\r\n')[0].strip().split(' ')
        self.header = {'method': self.type[0], 'link': ' '.join(self.type[1:-1]), 'ver': self.type[-1],
                       'data': {'user-agent': '', 'Accept': '', 'Accept-Encoding': '', 'Accept-Language': ''}}
        header = self.parse_http_header(header)
        self.payload = b''
        self.files = []
        self.header['data'].update(header)
        self.ip, self.port = client_address[:2]
        self.protocol = self.header['ver'].split('/')[0]
        self.method = self.header['method']
        self.version = self.header['ver']
        self.full_link = urllib.parse.unquote_plus(self.header['link'].replace('+', ' '))
        self.headers = self.header['data']
        self.host = self.headers['Host']
        self.user_agent = self.headers['User-Agent'] if 'User-Agent' in self.headers.keys() else \
            self.headers['user-agent']
        self.accept = self.headers['Accept'].split(',')
        self.encoding = self.headers['Accept-Encoding'].split(',')
        self.language = self.headers['Accept-Language'].split(',')
        self.link = self.full_link[:(self.full_link.index('?') if '?' in self.full_link else None)]
        self.args = get_args(
            self.full_link[(self.full_link.index('?') + 1 if '?' in self.full_link else len(self.full_link)):])
        self.cookies = {c.split('=')[0].strip(): c.split('=')[1] for c in
                        self.headers['Cookie'].split(';')} if 'Cookie' in self.headers else dict()
        self.content_length = int(self.headers.get('Content-Length', '0'))
        self.content_type = self.headers.get('Content-Type', '').split(';')[0], dict([
            tuple(arg.strip().split('='))
            for arg in self.headers.get('Content-Type', '').split(';')[1:]
        ])

        self.__str__ = self.__repr__

        self.connection = connection
        self.server = server
        self.htrf = htrf
        self.body = RequestBody(self)

    def __repr__(self) -> str:
        return f'[{self.method}] request {self.full_link} from {"" if "." in self.ip else "["}{self.ip}{"" if "." in self.ip else "]"}:{self.port} on {self.host}'

    def respond(self, response_class, *args, **kwargs) -> None:
        made = utils.optional(response_class(*args, **kwargs).make, version = self.version, htrf = self.htrf)
        if made is None:
            return
        self.connection.send(made)

    def recv(self, n_bytes: int) -> bytes:
        return self.connection.recv(n_bytes)
    
    def WebSocket(self):
        conn = WebSocketConnection(self)
        conn.handshake()
        return conn


class RequestBody:
    def __init__(self, request):
        self._request = request
        self._received = 0
        self._pending = True

    def size(self):
        return self._request.content_length

    def end(self):
        return self._received >= self.size() or not self._pending

    def recv(self, n_bytes):
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

    def getline(self):
        line = bytearray()
        while b := self.recv(self._request.server.max_bytes_per_receive):
            if b'\r\n' in b:
                lines = b.split(b'\r\n')
                line += lines[0]
                self._request.connection.paste(b[len(lines[0])+2:])
                break
            line += b
        return line

    def get(self):
        data = bytearray()
        while b := self.recv(self._request.server.max_bytes_per_receive):
            data += b
        self._received = len(data)
        return bytes(data)

    def files_boundary(self):
        return self._request.content_type[1].get('boundary', None)

    def next_file_header(self):
        while line := self.getline():
            if line == b'--' + self.files_boundary().encode():
                break
        header = []
        while line := self.getline():
            header.append(line)
        return Request.parse_http_header(b'\r\n'.join(header).decode())

    def next_file_body(self):
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
