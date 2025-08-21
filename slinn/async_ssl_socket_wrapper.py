import ssl
import errno
import select
import asyncio


class AsyncSSLSocketWrapper:
    def __init__(self, sock, ssl_context, loop, timeout=None):
        self._sock = sock
        self.loop = loop
        self._sock.setblocking(False)

        self._in_bio = ssl.MemoryBIO()
        self._out_bio = ssl.MemoryBIO()
        self._ssl_obj = ssl_context.wrap_bio(
            self._in_bio,
            self._out_bio,
            server_side=True
        )
        self._handshake_complete = False

        self._timeout = 0 if timeout is None else timeout
        self.buffer = bytearray()

    async def do_handshake(self):
        while not self._handshake_complete:
            try:
                self._ssl_obj.do_handshake()
                self._handshake_complete = True
                await self._flush_out_bio()
                return
            except ssl.SSLWantReadError:
                await self._process_handshake_read()
            except ssl.SSLWantWriteError:
                await self._process_handshake_write()

    async def _process_handshake_read(self):
        if self._out_bio.pending:
            await self._flush_out_bio()

        await self._feed_in_bio()

    async def _process_handshake_write(self):
        await self._flush_out_bio()

        if self._sock in select.select([self._sock], [], [], self._timeout)[0]:
            await self._feed_in_bio()

    async def _feed_in_bio(self):
        try:
            data = await self.loop.sock_recv(self._sock, 16384)
            if not data:
                raise
            self._in_bio.write(data)
        except BlockingIOError:
            pass
        except OSError as e:
            if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                raise

    async def _flush_out_bio(self):
        while self._out_bio.pending and self.fileno() != -1:
            data = self._out_bio.read()
            if data:
                await self.loop.sock_sendall(self._sock, data)

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
        if not self._handshake_complete:
            await self.do_handshake()

        while True:
            try:
                data = self._ssl_obj.read(n_bytes)
                if not data:
                    return b''
                return data
            except ssl.SSLWantReadError:
                await asyncio.wait_for(self._process_handshake_read(), self._timeout)
            except ssl.SSLWantWriteError:
                await asyncio.wait_for(self._process_handshake_write(), self._timeout)
            except ssl.SSLZeroReturnError:
                return b''

    async def send(self, data):
        if not self._handshake_complete:
            await self.do_handshake()

        total_sent = 0
        while total_sent < len(data):
            try:
                sent = self._ssl_obj.write(data[total_sent:])
                total_sent += sent
                await self._flush_out_bio()
            except ssl.SSLWantReadError:
                await self._process_handshake_read()
            except ssl.SSLWantWriteError:
                await self._process_handshake_write()

    def paste(self, data):
        self.buffer = data + self.buffer

    def settimeout(self, timeout):
        self._sock.settimeout(timeout)
        self._timeout = timeout

    def setblocking(self, blocking):
        self._sock.setblocking(blocking)

    def getsockopt(self, *args):
        return self._sock.getsockopt(*args)

    def fileno(self):
        return self._sock.fileno()

    async def close(self):
        try:
            if self._handshake_complete:
                try:
                    self._ssl_obj.unwrap()
                except ssl.SSLWantReadError:
                    pass
            await self._flush_out_bio()
        finally:
            self._sock.close()