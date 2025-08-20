class SSLSocketWrapper:
    def __init__(self, sock, ssl_context):
        self._sock = sock
        self.ssl_context = ssl_context
        sock = self.ssl_context.wrap_socket(sock, server_side=True,
                                            do_handshake_on_connect=True, suppress_ragged_eofs=True)
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
        self.buffer += data

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
