from __future__ import annotations
from . import Request, RequestBody, AsyncWebSocketConnection, TCPResponseChunk, FTDispatcher, AsyncSocketWrapper, utils
from typing import Optional
import urllib.parse
import socket
import asyncio


class AsyncRequest(Request):
    """
    Representation of HTTP request from client
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        header: str,
        client_address: tuple[str, int],
        connection: AsyncSocketWrapper,
        server: 'AsyncServer',
        htrf: Optional[FTDispatcher] = None,
    ):
        super().__init__(
            header=header,
            client_address=client_address,
            connection=connection,
            server=server,
            htrf=htrf
        )
        self.loop = loop
        self.body = AsyncRequestBody(self)

    async def respond(
        self,
        response_class: type[TCPResponseChunk],
        *args,
        **kwargs
    ) -> None:
        buffer = utils.optional(response_class(*args, **kwargs).make, version=self.version, htrf=self.htrf)
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

    async def WebSocket(self, timeout: float) -> AsyncWebSocketConnection:
        conn = AsyncWebSocketConnection(self)
        await conn.handshake()
        conn.settimeout(timeout)
        return conn


class AsyncRequestBody(RequestBody):
    _request: AsyncRequest

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
                for key, val in Request.get_args((await self.getline()).decode()).items()
            }
        return {}

    async def skip(self):
        while not self.end():
            await self.receive()

    async def next_file_header(self) -> dict:
        while line := await self.getline():
            if line == b'--' + self.files_boundary().encode():
                break
        header = []
        while line := await self.getline():
            header.append(line)
        return Request.parse_http_header(b'\r\n'.join(header).decode())

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
