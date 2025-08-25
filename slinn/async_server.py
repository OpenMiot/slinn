from __future__ import annotations
from typing import Any
from . import AsyncRequest, Address, Filter, HCDispatcher, FTDispatcher, utils, AsyncSSLSocketWrapper, AsyncSocketWrapper, exceptions
import asyncio
import socket
import ssl
import os
import logging
import traceback
import warnings


class AsyncServer:
    """
    Main class to start async server
    """

    class Handle:
        def __init__(self, filter: Filter, function):
            self.filter = filter
            self.function = function

    def __init__(self, *dispatchers: tuple[Any, ...], smart_navigation: bool = True, ssl_fullchain: str = None,
                 # type: ignore
                 ssl_key: str = None, timeout: float = 0.03, max_bytes_per_receive: int = 4096,
                 max_header_size: int = 4294967296, _func=lambda server: None, logger: logging.Logger = logging.getLogger(),
                 hcdp: HCDispatcher = HCDispatcher(), htrf: FTDispatcher = FTDispatcher()) -> None:  # type: ignore
        self.dispatchers = dispatchers
        self.smart_navigation = smart_navigation
        self.server_socket = None
        self.ssl = ssl_fullchain is not None and ssl_key is not None
        self.ssl_cert, self.ssl_key = ssl_fullchain, ssl_key
        self.ssl_context = None
        self.thread = None
        self.timeout = timeout
        self.max_bytes_per_receive = max_bytes_per_receive
        self.max_header_size = max_header_size
        self._func = _func
        self.logger = logger
        self.hcdp = hcdp
        self.htrf = htrf

        self.loop: asyncio.EventLoop = None

    def reload(self, *dispatchers: tuple) -> None:
        if self.thread is not None:
            self.thread.stop()
            try:
                self.thread.join()
            except RuntimeError:
                pass
        self.dispatchers = dispatchers
        self.logger.info('Server has reloaded')

    def address(self, port: int, domain: str = None):
        protocol = 'https' if self.ssl else 'http'
        return (f'{protocol.upper()} server is available on {protocol}://' +
                ('0.0.0.0' if (domain is None or domain == '') else ('[' + domain + ']' if ':' in domain else domain)) +
                f'{(":" + str(port) if port != 443 else "") if self.ssl else (":" + str(port) if port != 80 else "")}/')

    async def listen(self, address: Address):
        self.server_socket = None
        self.loop = asyncio.get_event_loop()
        if ':' in address.host:
            self.server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            if socket.has_dualstack_ipv6():
                self.server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        else:
            self.server_socket = socket.socket(socket.AF_INET if '.' in address.host else socket.AF_INET6,
                                               socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((address.host, address.port))
        except PermissionError:
            self.logger.critical(f'Permission denied')
            exit(13)
        if self.ssl:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            self.ssl_context.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)
        self.server_socket.settimeout(self.timeout)
        self.server_socket.listen()
        self.server_socket.setblocking(False)
        self.logger.info('Server started to listening')
        print(self.address(address.port, address.domain))
        try:
            while True:
                try:
                    connection, client_address = await self.loop.sock_accept(self.server_socket)
                    self.loop.create_task(self.handle_request(connection, client_address))
                except (BlockingIOError, socket.timeout):
                    await asyncio.sleep(0.01)
                except Exception as e:
                    self.logger.warning(f'During handling exception, an {e} has occurred')
                    self.logger.warning(traceback.format_exc())
                    self.reload(*self.dispatchers)
                    
        except KeyboardInterrupt:
            self.logger.critical('Got KeyboardInterrupt, halting the application...')
            if utils.check_socket(self.server_socket):
                self.server_socket.close()
            os._exit(0)

    async def handle_request(self, connection: socket.socket, client_address):
        try:
            self._func(self)
            connection = (AsyncSSLSocketWrapper(connection, self.ssl_context, self.loop)
                            if self.ssl else
                          AsyncSocketWrapper(connection, self.loop))
            try:
                connection.settimeout(self.timeout)
                data = bytearray()
                while len(data) < self.max_header_size and b'\r\n\r\n' not in data:
                    try:
                        b = await connection.recv(self.max_bytes_per_receive)
                        data += b
                    except (TimeoutError, socket.timeout, asyncio.exceptions.TimeoutError):
                        break
                data = data.split(b'\r\n\r\n')
                header = data[0].decode()
                if header == '':
                    return
                request = AsyncRequest(self.loop, header, client_address, connection, self)
                request.htrf = self.htrf
                self.logger.info(repr(request))
                request.connection.paste(b'\r\n\r\n'.join(data[1:]))
            except KeyError:
                return self.logger.info('Got KeyError, probably invalid request. Ignore')
            except UnicodeDecodeError:
                return self.logger.info('Got UnicodeDecodeError, probably invalid header. Ignore')
            except ConnectionResetError:
                return self.logger.info('Connection reset by client')
            except OSError:
                return self.logger.info('Connection closed')
            for dispatcher in self.dispatchers:
                if True in [utils.restartswith(request.host, host) for host in dispatcher.hosts]:
                    if self.smart_navigation:
                        sizes = [handle.filter.size(request.link, request.method) for handle in dispatcher.handles]
                        if sizes:
                            if await self.answer_request(connection, dispatcher.handles[sizes.index(max(sizes))], request,
                                                         data, header):
                                return
                    else:
                        for handle in dispatcher.handles:
                            if await self.answer_request(connection, handle, request, data, header):
                                return
            try:
                return await self.answer_request(connection, self.hcdp[404], request, data, header)
            except exceptions.HandlerNotFound:
                warnings.warn('Error code 404 `s handler is not defined', exceptions.Handler404NotFound)
            await connection.close()
        except Exception as exception:
            self.logger.warning(f'During handling request, an {exception} has occurred')
            self.logger.warning(traceback.format_exc())
            self.reload(*self.dispatchers)
            try:
                return await self.answer_request(connection, self.hcdp[500], request, data, header)
            except UnboundLocalError:
                return await connection.close()
            except exceptions.HandlerNotFound:
                warnings.warn('Error code 500 `s handler is not defined', exceptions.Handler500NotFound)
            await connection.close()

    async def answer_request(self, connection, handle, request, http_data, http_header):
        if not handle.filter.check(request.link, request.method):
            return False
        if not utils.check_socket(connection):
            return True
        response = await utils.optional(handle.function,
                                        request=request,
                                        http_data=http_data,
                                        http_header=http_header,
                                        http_content=b'',
                                        client_socket=connection,
                                        server=self,
                                        **handle.args(request))
        if type(response) is int:
            handle = self.hcdp[response]
            if handle is not None:
                return await self.answer_request(connection, handle, request, http_data, http_header)
            self.logger.error(f'Error code {response} `s handler is not defined')
        elif response is not None:
            buffer = utils.optional(response.make, version=request.version, type=request.version, gzip=False,
                                    htrf=self.htrf)
            packages = [buffer[x:x + self.max_bytes_per_receive] for x in
                        range(0, len(buffer), self.max_bytes_per_receive)]
            i = 0
            while i < len(packages):
                try:
                    await connection.send(packages[i])
                    i += 1
                except TimeoutError:
                    continue
        await connection.close()
        return True
