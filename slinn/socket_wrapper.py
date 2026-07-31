from .exceptions import SocketClosed
import asyncio
import socket


class SocketWrapper:
    class _Protocol(asyncio.Protocol):
        def __init__(self, on_data_received):
            self.on_data_received = on_data_received
            self.transport = None
            self.buffer = bytearray()

        def data_received(self, data):
            self.buffer.extend(data)
            self.on_data_received(data)

    def __init__(self, sock: socket.socket, loop: asyncio.AbstractEventLoop, timeout: float = 5):
        self._sock = sock
        self.buffer = bytearray()
        self._timeout = timeout
        self.loop = loop
        self._transport, self._protocol = None, None
        self._read_event = asyncio.Event()
        self._handshake_complete = False
        self.sendall = self.send

    async def do_handshake(self):
        if self._handshake_complete:
            return

        def _data_received_callback(data):
            if type(self.buffer) == bytes:
                self.buffer = bytearray(self.buffer)
            self.buffer.extend(data)
            self._read_event.set()

        def _protocol_factory():
            return SocketWrapper._Protocol(_data_received_callback)

        self._transport, self._protocol = await self.loop.create_connection(_protocol_factory, sock=self._sock)
        self._handshake_complete = True

    async def recv(self, n_bytes: int):
        await self.do_handshake()

        if not self.buffer:
            await asyncio.wait_for(self._read_event.wait(), timeout=self._timeout)

        self._read_event.clear()

        data = self.buffer[:n_bytes] if len(self.buffer) > n_bytes else self.buffer
        self.buffer = self.buffer[n_bytes:] if len(self.buffer) > n_bytes else bytearray()
        return data

    async def send(self, data: bytes):
        if self.closed():
            raise SocketClosed('socket closed')
        await self.do_handshake()
        self._transport.write(data)

    def paste(self, data: bytes):
        self.buffer = data + self.buffer

    def settimeout(self, timeout: float):
        self._timeout = timeout

    def setblocking(self, blocking: bool):
        return self._sock.setblocking(blocking)

    def getsockopt(self, *args) -> int | bytes:
        return self._sock.getsockopt(*args)

    def fileno(self) -> int:
        return self._sock.fileno()

    def close(self):
        if self._transport:
            self._transport.close()

    def closed(self) -> bool:
        return self.fileno() == -1
