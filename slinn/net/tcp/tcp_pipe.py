from __future__ import annotations
from slinn.net import PipeProtocol
from slinn.exceptions import SocketClosed
from slinn.net.address import Address, TransportProtocol
from typing import Optional, Any
import asyncio
import socket
import ssl


class TcpPipe(PipeProtocol):
    class _Protocol(asyncio.Protocol):
        def __init__(self, on_data_received):
            self.on_data_received = on_data_received
            self.transport = None
            self.buffer = bytearray()

        def data_received(self, data):
            self.buffer.extend(data)
            self.on_data_received(data)

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        *,
        family: socket.AddressFamily | int = -1,
        type: socket.SocketKind | int = -1,
        proto: int = -1,
        fileno: Optional[int] = None,
        timeout: float = 5,
        ssl_context: Optional[ssl.SSLContext] = None,
        bytes_per_receive: int = 65536
    ):
        self._sock = socket.socket(family, type, proto, fileno)
        self.buffer = bytearray()
        self._timeout = timeout
        self.loop = loop
        self.ssl_context = ssl_context
        self._bytes_per_receive = bytes_per_receive

        self._transport, self._protocol = None, None
        self._read_event = asyncio.Event()
        self._handshake_complete = False

        self.set_blocking(False)

    async def do_handshake(self):
        if self._handshake_complete:
            return

        def _data_received_callback(data):
            if type(self.buffer) == bytes:
                self.buffer = bytearray(self.buffer)
            self.buffer.extend(data)
            self._read_event.set()

        def _protocol_factory():
            return TcpPipe._Protocol(_data_received_callback)

        self._transport, self._protocol = await self.loop.create_connection(_protocol_factory, sock=self._sock)
        if self.ssl_context:
            self._transport = await self.loop.start_tls(
                self._transport,
                self._protocol,
                self.ssl_context,
                server_side=True
            )
        self._handshake_complete = True

    async def recv(self, n_bytes: Optional[int] = None):
        if n_bytes is None:
            n_bytes = self._bytes_per_receive

        await self.do_handshake()

        if not self.buffer:
            await asyncio.wait_for(self._read_event.wait(), timeout=self._timeout)

        if not self.buffer:
            self.close()
            raise SocketClosed('socket closed')

        self._read_event.clear()

        data = self.buffer[:n_bytes] if len(self.buffer) > n_bytes else self.buffer
        self.buffer = self.buffer[n_bytes:] if len(self.buffer) > n_bytes else bytearray()
        return data

    async def send(self, data: bytes) -> None:
        await self.do_handshake()

        if self.closed:
            raise SocketClosed('socket closed')
        await self.do_handshake()
        try:
            self._transport.write(data)
        except (OSError, ConnectionResetError):
            self.close()
            raise SocketClosed('socket closed')

    def paste(self, data: bytes) -> None:
        self.buffer = data + self.buffer

    def bind(self, address: tuple[Any, ...] | str | Any):
        self._sock.bind(address)

    def listen(self, backlog: int = socket.SOMAXCONN) -> None:
        self._sock.listen(backlog)

    async def accept(self) -> tuple[TcpPipe, Address]:
        client_sock, client_address = await self.loop.sock_accept(self._sock)
        client_pipe = TcpPipe(
            self.loop,
            fileno=client_sock.detach(),
            timeout=self._timeout,
            ssl_context=self.ssl_context
        )
        await client_pipe.do_handshake()
        return client_pipe, Address(
            port = client_address[1],
            transport_protocol = TransportProtocol.TCP,
            host = client_address[0]
        )

    def set_timeout(self, timeout: float) -> None:
        self._timeout = timeout

    def set_blocking(self, blocking: bool):
        self._sock.setblocking(blocking)

    def get_sock_opt(self, *args) -> int | bytes:
        return self._sock.getsockopt(*args)

    def set_sock_opt(self, level: int, opt_name: int, value: int | Any):
        self._sock.setsockopt(level, opt_name, value)

    def file_no(self) -> int:
        return self._sock.fileno()

    def close(self) -> None:
        if self._transport:
            self._transport.close()

    @property
    def closed(self) -> bool:
        return self.file_no() == -1 or (self._transport and self._transport.is_closing())
