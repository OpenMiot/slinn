from . import WebSocketFrame, WebSocketOpcodes, WebSocketHandshake, AsyncRequest, HttpResponseChunk, utils
from .exceptions import NotAWebSocketConnection


class AsyncWebSocketConnection:
    def __init__(self, request: AsyncRequest):
        self.request = request
        self.closed = False

    async def handshake(self):
        if 'Sec-WebSocket-Key' not in self.request.headers:
            raise NotAWebSocketConnection()
        await self.request.respond(WebSocketHandshake, self.request.headers['Sec-WebSocket-Key'])

    async def _send(self, opcode: WebSocketOpcodes, payload: bytes):
        frame = WebSocketFrame(True, opcode, False, payload)
        await self.request.respond(HttpResponseChunk, WebSocketFrame.pack(frame))

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

    async def send(self, payload):
        if type(payload) == bytes:
            await self.send_binary(payload)
        elif type(payload) == str:
            await self.send_text(payload)
        else:
            raise TypeError()

    async def read(self):
        data = bytearray(await self.request.recv(2))
        payload_len = data[1] & 127
        if payload_len == 126:
            data += await self.request.recv(2)
            payload_len = data[2:4]
        elif payload_len == 127:
            data += await self.request.recv(4)
            payload_len = data[2:6]
        if data[1] & 128:
            data += await self.request.recv(4)
        if payload_len < 126:
            data += await self.request.recv(payload_len)
        elif 125 < payload_len < 65536:
            data += await self.request.recv(payload_len)
        else:
            data += await self.request.recv(payload_len)
        frame = WebSocketFrame.unpack(data)
        if frame.opcode == WebSocketOpcodes.CLOSE:
            self.closed = True
            if utils.check_socket(self.request.connection):
                self.request.connection.close()
        return frame
