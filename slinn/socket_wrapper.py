from .exceptions import SocketClosed
import socket


class SocketWrapper:
    def __init__(self, sock: socket.socket, timeout: float = 5):
        self._sock = sock
        self.buffer = bytearray()
        self.sendall = self.send
        self._timeout = timeout

    def recv(self, n_bytes: int) -> bytes:
        if len(self.buffer) > 0:
            if len(self.buffer) > n_bytes:
                data = self.buffer[:n_bytes]
                self.buffer = self.buffer[n_bytes:]
                return data
            else:
                data = self.buffer
                self.buffer = bytearray()
                return data
        return self._sock.recv(n_bytes)

    def send(self, data: bytes) -> int:
        if self.closed():
            raise SocketClosed('socket closed')
        return self._sock.send(data)

    def paste(self, data: bytes):
        self.buffer = data + self.buffer

    def settimeout(self, timeout: float):
        self._timeout = timeout
        return self._sock.settimeout(timeout)

    def setblocking(self, blocking: bool):
        return self._sock.setblocking(blocking)

    def getsockopt(self, *args) -> int | bytes:
        return self._sock.getsockopt(*args)

    def fileno(self) -> int:
        return self._sock.fileno()

    def close(self):
        return self._sock.close()

    def closed(self) -> bool:
        return self.fileno() == -1
