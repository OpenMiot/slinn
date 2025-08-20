import asyncio, socket

class AsyncSocketWrapper:
    def __init__(self, sock, loop, timeout=None):
        self._sock = sock
        self.loop = loop
        self.timeout = timeout
        self.buffer = bytearray()

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
            if self.timeout is not None:
                return await asyncio.wait_for(self.loop.sock_recv(self._sock, n_bytes), self.timeout)
            return await self.loop.sock_recv(self._sock, n_bytes)
        except (asyncio.TimeoutError, TimeoutError):
            raise socket.timeout("recv timed out")

    async def send(self, data):
        await self.loop.sock_sendall(self._sock, data)

    def paste(self, data):
        self.buffer += data

    def settimeout(self, timeout):
        self._sock.settimeout(timeout)
        self.timeout = timeout

    def setblocking(self, blocking):
        self._sock.setblocking(blocking)

    def getsockopt(self, *args):
        return self._sock.getsockopt(*args)

    def fileno(self):
        return self._sock.fileno()

    async def close(self):
        self._sock.close()
