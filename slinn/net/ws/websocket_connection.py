from __future__ import annotations
from slinn.net.ws import WebSocketFrame, WebSocketOpcodes, WebSocketHandshake
from slinn.net.http.responses import HttpChunkResponse
from slinn.exceptions import NotAWebSocketConnection


class WebSocketConnection:
    def __init__(self, request: 'HttpRequest'):
        self.request = request
        self.client_pipe = request.client_pipe

    async def handshake(self):
        if 'Sec-WebSocket-Key' not in self.request.headers:
            raise NotAWebSocketConnection()
        await self.client_pipe.send(
            WebSocketHandshake(self.request.headers['Sec-WebSocket-Key']).make(self.request.version)
        )

    async def _send(self, opcode: WebSocketOpcodes, payload: bytes):
        frame = WebSocketFrame(True, opcode, False, payload)
        await self.client_pipe.send(HttpChunkResponse(WebSocketFrame.pack(frame)).make())

    async def send_binary(self, payload: bytes):
        await self._send(WebSocketOpcodes.BINARY, payload)

    async def send_text(self, payload: str):
        await self._send(WebSocketOpcodes.TEXT, payload.encode())

    async def ping(self):
        await self._send(WebSocketOpcodes.PING, b'')

    async def pong(self):
        await self._send(WebSocketOpcodes.PONG, b'')

    async def close(self, reason: str = ''):
        await self._send(WebSocketOpcodes.CLOSE, reason.encode())

    def set_timeout(self, timeout: float):
        self.client_pipe.set_timeout(timeout)

    @property
    def closed(self) -> bool:
        return self.client_pipe.closed

    async def send(self, payload: bytes | str):
        if isinstance(payload, bytes):
            await self.send_binary(payload)
        elif isinstance(payload, str):
            await self.send_text(payload)
        else:
            raise TypeError()

    async def read(self) -> WebSocketFrame:
        data = bytearray(await self.client_pipe.recv(2))
        payload_len = data[1] & 127
        if payload_len == 126:
            data += await self.client_pipe.recv(2)
            payload_len = int.from_bytes(data[2:4])
        elif payload_len == 127:
            data += await self.client_pipe.recv(4)
            payload_len = int.from_bytes(data[2:6])
        if data[1] & 128:
            data += await self.client_pipe.recv(4)
        if payload_len < 126:
            data += await self.client_pipe.recv(payload_len)
        elif 125 < payload_len < 65536:
            data += await self.client_pipe.recv(payload_len)
        else:
            data += await self.client_pipe.recv(payload_len)
        frame = WebSocketFrame.unpack(data)
        if frame.opcode == WebSocketOpcodes.CLOSE:
            if not self.closed:
                self.client_pipe.connection.close()
        return frame
