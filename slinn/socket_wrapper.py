class SocketWrapper:
    def __init__(self, sock):
        self._sock = sock
        self.buffer = bytearray()

    def recv(self, n_bytes):
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

    def send(self, data):
        return self._sock.send(data)

    def paste(self, data):
        self.buffer = data + self.buffer

    def settimeout(self, timeout):
        return self._sock.settimeout(timeout)

    def setblocking(self, blocking):
        return self._sock.setblocking(blocking)

    def getsockopt(self, *args):
        return self._sock.getsockopt(*args)

    def fileno(self):
        return self._sock.fileno()

    def close(self):
        return self._sock.close()
