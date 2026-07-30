from . import SocketWrapper
import socket
import ssl


class SSLSocketWrapper(SocketWrapper):
    def __init__(self, sock: socket.socket, ssl_context: ssl.SSLContext, timeout: float = 5):
        SocketWrapper.__init__(self, sock, timeout)
        self.ssl_context = ssl_context
        self._sock = self.ssl_context.wrap_socket(self._sock, server_side=True,
                                                  do_handshake_on_connect=True, suppress_ragged_eofs=True)
