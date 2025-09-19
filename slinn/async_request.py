from . import Request, RequestBody, AsyncWebSocketConnection, utils
import asyncio
import socket


class AsyncRequest(Request):
    """
    Representation of HTTP request from client
    """

    def __init__(self, loop, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.body = AsyncRequestBody(self)

    async def respond(self, response_class, *args, **kwargs) -> None:
        buffer = utils.optional(response_class(*args, **kwargs).make, version = self.version, htrf = self.htrf)
        if buffer is None:
            return
        packages = [buffer[x:x + self.server.max_bytes_per_receive] for x in
                    range(0, len(buffer), self.server.max_bytes_per_receive)]
        i = 0
        while i < len(packages):
            try:
                await self.connection.send(packages[i])
                i += 1
            except TimeoutError:
                continue

    async def recv(self, n_bytes: int) -> bytes:
        return await self.connection.recv(n_bytes)
    
    async def WebSocket(self):
        conn = AsyncWebSocketConnection(self)
        await conn.handshake()
        return conn

class AsyncRequestBody(RequestBody):
    async def recv(self, n_bytes):
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

    async def getline(self):
        line = bytearray()
        while b := await self.recv(self._request.server.max_bytes_per_receive):
            if b'\r\n' in b:
                lines = b.split(b'\r\n')
                line += lines[0]
                self._request.connection.paste(b[len(lines[0])+2:])
                break
            line += b
        return line

    async def get(self):
        data = bytearray()
        while b := await self.recv(self._request.server.max_bytes_per_receive):
            data += b
        self._received = len(data)
        return bytes(data)

    async def next_file_header(self):
        while line := await self.getline():
            if line == b'--' + self.files_boundary().encode():
                break
        header = []
        while line := await self.getline():
            header.append(line)
        return Request.parse_http_header(b'\r\n'.join(header).decode())

    async def next_file_body(self):
        data = bytearray()
        while line := await self.getline():
            if line == b'--' + self.files_boundary().encode():
                self._request.connection.paste(b'--' + self.files_boundary().encode() + b'\r\n')
                break
            if line == b'--' + self.files_boundary().encode() + b'--':
                self._pending = False
                break
            data += line
        return bytes(data)
