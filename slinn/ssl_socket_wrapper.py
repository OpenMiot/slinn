from . import SocketWrapper
import asyncio
import socket
import ssl


class SSLSocketWrapper(SocketWrapper):
    def __init__(
        self,
        sock: socket.socket,
        ssl_context: ssl.SSLContext,
        loop: asyncio.AbstractEventLoop,
        timeout: float = 5
    ):
        SocketWrapper.__init__(self, sock, loop, timeout)
        self.ssl_context = ssl_context
    
    async def do_handshake(self):
        if self._handshake_complete:
            return

        def _data_received_callback(data):
            if type(self.buffer) == bytes:
                self.buffer = bytearray(self.buffer)
            self.buffer.extend(data)
            self._read_event.set()

        def _protocol_factory():
            return SSLSocketWrapper._Protocol(_data_received_callback)
        
        self._transport, self._protocol = await self.loop.create_connection(_protocol_factory, sock=self._sock)
        self._transport = await self.loop.start_tls(self._transport, self._protocol, self.ssl_context, server_side=True)
        self._handshake_complete = True
