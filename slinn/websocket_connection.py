from . import WebSocketFrame, WebSocketOpcodes, WebSocketHandshake, Request, HttpResponseChunk, utils
from .exceptions import NotAWebSocketConnection


class WebSocketConnection:
    def __init__(self, request: Request):
        self.request = request
        self.closed = False

    def handshake(self):
        if 'Sec-WebSocket-Key' not in self.request.headers:
            raise NotAWebSocketConnection()
        self.request.respond(WebSocketHandshake, self.request.headers['Sec-WebSocket-Key'])

    def _send(self, opcode: WebSocketOpcodes, payload: bytes):
        frame = WebSocketFrame(True, opcode, False, payload)
        self.request.respond(HttpResponseChunk, WebSocketFrame.pack(frame))

    def send_binary(self, payload: bytes):
        self._send(WebSocketOpcodes.BINARY, payload)

    def send_text(self, payload: str):
        self._send(WebSocketOpcodes.TEXT, payload.encode())

    def ping(self):
        self._send(WebSocketOpcodes.PING, b'')

    def pong(self):
        self._send(WebSocketOpcodes.PONG, b'')

    def close(self, reason: str = ''):
        self._send(WebSocketOpcodes.CLOSE, reason.encode())

    def send(self, payload):
        if type(payload) == bytes:
            self.send_binary(payload)
        elif type(payload) == str:
            self.send_text(payload)
        else:
            raise TypeError()

    def read(self):
        data = bytearray(self.request.recv(2))
        payload_len = data[1] & 127
        if payload_len == 126:
            data += self.request.recv(2)
            payload_len = data[2:4]
        elif payload_len == 127:
            data += self.request.recv(4)
            payload_len = data[2:6]
        if data[1] & 128:
            data += self.request.recv(4)
        if payload_len < 126:
            data += self.request.recv(payload_len)
        elif 125 < payload_len < 65536:
            data += self.request.recv(payload_len)
        else:
            data += self.request.recv(payload_len)
        frame = WebSocketFrame.unpack(data)
        if frame.opcode == WebSocketOpcodes.CLOSE:
            self.closed = True
            if utils.check_socket(self.request.connection):
                self.request.connection.close()
        return frame
