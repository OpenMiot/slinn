from . import AsyncSocketWrapper


class AsyncSSLSocketWrapper(AsyncSocketWrapper):
    def __init__(self, sock, ssl_context, loop):
        AsyncSocketWrapper.__init__(self, sock, loop)
        self.ssl_context = ssl_context
        self._sock = self.loop.start_tls(self._sock, self._sock.get_protocol(), self.ssl_context, server_side=True,
                                         do_handshake_on_connect=True, suppress_raged_eofs=True)
