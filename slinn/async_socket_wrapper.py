import asyncio

class AsyncSocketWrapper:
    def __init__(self, sock, loop):
        self._sock = sock
        self.loop = loop

    async def recv(self, n_bytes):
        return await self.loop.sock_recv(self._sock, n_bytes)

    async def send(self, data):
        await self.loop.sock_sendall(self._sock, data)
    
    def settimeout(self, timeout):
        self._sock.settimeout(timeout)
    
    def setblocking(self, blocking):
        self._sock.setblocking(blocking)
    
    def getsockopt(self, *args):
        return self._sock.getsockopt(*args)
    
    def fileno(self):
        return self._sock.fileno()
    
    def close(self):
        self._sock.close()
