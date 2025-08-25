import asyncio, socket
from . import SocketWrapper

class AsyncSocketWrapper(SocketWrapper):
    def __init__(self, sock, loop):
        SocketWrapper.__init__(self, sock)
        self.loop = loop
        self._timeout = None

    async def recv(self, n_bytes):
        if len(self.buffer) > 0:
            if len(self.buffer) > n_bytes:
                data = self.buffer[:n_bytes]
                self.buffer = self.buffer[n_bytes:]
                return data
            else:
                data = self.buffer
                self.buffer = bytearray()
                return data
        try:
            if self._timeout is not None:
                return await asyncio.wait_for(self.loop.sock_recv(self._sock, n_bytes), self._timeout)
            return await self.loop.sock_recv(self._sock, n_bytes)
        except (asyncio.TimeoutError, TimeoutError):
            raise socket.timeout("recv timed out")

    async def send(self, data):
        await self.loop.sock_sendall(self._sock, data)

    def settimeout(self, timeout):
        self._sock.settimeout(timeout)
        self._timeout = timeout

    async def close(self):
        self._sock.close()
