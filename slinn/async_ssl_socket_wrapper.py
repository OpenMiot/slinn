from . import AsyncSocketWrapper
import asyncio


class AsyncSSLSocketWrapper(AsyncSocketWrapper):
    class _Protocol(asyncio.Protocol):
        def __init__(self, on_data_received):
            self.on_data_received = on_data_received
            self.transport = None
            self.buffer = bytearray()

        def data_received(self, data):
            self.buffer.extend(data)
            self.on_data_received(data)

    def __init__(self, sock, ssl_context, loop):
        AsyncSocketWrapper.__init__(self, sock, loop)
        self.ssl_context = ssl_context
        self._transport, self._protocol = None, None
        self._read_event = asyncio.Event()
        self._handshake_complete = False

    async def do_handshake(self):
        if self._handshake_complete:
            return

        def _data_received_callback(data):
            if type(self.buffer) == bytes:
                self.buffer = bytearray(self.buffer)
            self.buffer.extend(data)
            self._read_event.set()

        def _protocol_factory():
            return AsyncSSLSocketWrapper._Protocol(_data_received_callback)
        
        self._transport, self._protocol = await self.loop.create_connection(_protocol_factory, sock=self._sock)
        self._transport = await self.loop.start_tls(self._transport, self._protocol, self.ssl_context, server_side=True)
        self._handshake_complete = True
    
    async def recv(self, n_bytes):
        await self.do_handshake()

        while len(self.buffer) == 0:
            await asyncio.sleep(0.001)
        
        if len(self.buffer) > n_bytes:
            data = self.buffer[:n_bytes]
            self.buffer = self.buffer[n_bytes:]
            return data
        else:
            data = self.buffer
            self.buffer = bytearray()
            return data

    async def send(self, data):
        await self.do_handshake()
        self._transport.write(data)

    def settimeout(self, timeout):
        self._timeout = timeout
    
    def close(self):
        if self._transport:
            self._transport.close()
