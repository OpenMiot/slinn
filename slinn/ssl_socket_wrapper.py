from . import SocketWrapper


class SSLSocketWrapper(SocketWrapper):
    def __init__(self, sock, ssl_context):
        SocketWrapper.__init__(self, sock)
        self.ssl_context = ssl_context
        self._sock = self.ssl_context.wrap_socket(self._sock, server_side=True,
                                            do_handshake_on_connect=True, suppress_ragged_eofs=True)
