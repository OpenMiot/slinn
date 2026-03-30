from __future__ import annotations
from typing import Any
from . import AsyncRequest, Address, Filter, HCDispatcher, FTDispatcher, utils, AsyncSSLSocketWrapper, AsyncSocketWrapper, exceptions, Server
from .tools.debugger import ExceptionResponse
import asyncio
import socket
import ssl
import os
import logging
import traceback
import warnings
import inspect


class AsyncServer(Server):
    """
    Main class to start async server
    """

    def __init__(self, *dispatchers: Any, smart_navigation: bool = True, ssl_fullchain: str = None,
                 ssl_key: str = None, timeout: float = 5, max_bytes_per_receive: int = 4096,
                 max_header_size: int = 4294967296, _func: Callable = None, logger: logging.Logger = None,
                 hcdp: HCDispatcher = None, htrf: FTDispatcher = None,
                 max_requests: int = 200, debug: bool = True) -> None:  # type: ignore
        Server.__init__(
            self,
            *dispatchers,
            smart_navigation=smart_navigation,
            ssl_fullchain=ssl_fullchain,
            ssl_key=ssl_key,
            timeout=timeout,
            max_bytes_per_receive=max_bytes_per_receive,
            max_header_size=max_header_size,
            _func=_func,
            logger=logger,
            hcdp=hcdp,
            htrf=htrf,
            max_requests=max_requests,
            debug=debug)

        self.loop: asyncio.EventLoop = None

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
                except KeyboardInterrupt as e:
                    self.exit()
                except (BlockingIOError, socket.timeout):
                    await asyncio.sleep(0.005)
                except Exception as e:
                    self.logger.warning(f'During handling exception, an {e} has occurred')
                    self.logger.warning(traceback.format_exc())
                    self.reload(*self.dispatchers)
        except KeyboardInterrupt:
            self.exit()

    async def handle_request(self, connection, client_address, wrapped=False, timeout=None, max_requests=None):
        connection = (AsyncSSLSocketWrapper(connection, self.ssl_context, self.loop)
                      if self.ssl else
                      AsyncSocketWrapper(connection, self.loop))
        max_requests = max_requests or self.max_requests
        while not connection.closed():
            max_requests -= 1
            try:
                if max_requests == 0:
                    connection.close()
                    break
                self._func(self)
                try:
                    data = bytearray()
                    while len(data) < self.max_header_size and b'\r\n\r\n' not in data:
                        try:
                            b = await asyncio.wait_for(connection.recv(self.max_bytes_per_receive), timeout=timeout)
                            data += b
                            if not b:
                                break
                        except KeyboardInterrupt:
                            self.exit()
                        except (TimeoutError, socket.timeout, asyncio.exceptions.TimeoutError):
                            connection.close()
                            break
                    data = data.split(b'\r\n\r\n')
                    header = data[0].decode()
                    if not header:
                        connection.close()
                        break
                    request = AsyncRequest(self.loop, header, client_address, connection, self, htrf=self.htrf)
                    self.logger.info(repr(request))
                    request.connection.paste(b'\r\n\r\n'.join(data[1:]))
                except KeyError:
                    self.logger.info('Got KeyError, probably invalid request. Ignore')
                    continue
                except UnicodeDecodeError:
                    self.logger.info('Got UnicodeDecodeError, probably invalid header. Ignore')
                    continue
                except ConnectionResetError:
                    self.logger.info('Connection reset by client')
                    continue
                except OSError:
                    self.logger.info('Connection closed')
                    continue
                if self.smart_navigation:
                    handles = []
                    for dispatcher in self.dispatchers:
                        if dispatcher.check(request.host):
                            handles += dispatcher.handles
                    sizes = [handle.filter.size(request) for handle in handles]
                    if sizes:
                        if await self.answer_request(connection, handles[sizes.index(max(sizes))], request,
                                                        data, header, max_requests):
                            connection._timeout = request.keep_alive.get('timeout', connection._timeout)
                            max_requests = request.keep_alive.get('max', max_requests)
                            continue
                else:
                    _cont = False
                    for dispatcher in self.dispatchers:
                        if dispatcher.check(request.host):
                            for handle in dispatcher.handles:
                                if await self.answer_request(connection, handle, request, data, header, max_requests):
                                    connection._timeout = request.keep_alive.get('timeout', connection._timeout)
                                    max_requests = request.keep_alive.get('max', max_requests)
                                    _cont = True
                                    break
                        if _cont:
                            break
                    if _cont:
                        continue
                try:
                    await self.answer_request(connection, self.hcdp[404], request, data, header, max_requests)
                except exceptions.HandlerNotFound:
                    warnings.warn('Error code 404 `s handler is not defined', exceptions.Handler404NotFound)
                    await connection.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 13\r\n\r\n404 Not Found')
                connection._timeout = request.keep_alive.get('timeout', connection._timeout)
                max_requests = request.keep_alive.get('max', max_requests)
                continue
            except KeyboardInterrupt:
                self.exit()
            except Exception as exception:
                self.logger.warning(f'During handling request, an {exception} has occurred')
                self.logger.warning(traceback.format_exc())
                self.reload(*self.dispatchers)
                try:
                    if self.debug:
                        await connection.send(ExceptionResponse(exception, request).make())
                    else:
                        await self.answer_request(connection, self.hcdp[500], request, data, header, max_requests)
                        continue
                except UnboundLocalError:
                    max_requests += 1
                    continue
                except exceptions.HandlerNotFound:
                    warnings.warn('Error code 500 `s handler is not defined', exceptions.Handler500NotFound)
                    await connection.send(
                        b'HTTP/1.1 500 Internal Server Error\r\nContent-Length: 25\r\n\r\n500 Internal Server Error')
                connection._timeout = request.keep_alive.get('timeout', connection._timeout)
                max_requests = request.keep_alive.get('max', max_requests)
                continue

    async def answer_request(self, connection, handle, request, http_data, http_header, max_requests):
        if not handle.filter.check(request):
            return False
        if connection.closed():
            return True
        cor = utils.optional(handle.function,
                             request=request,
                             http_data=http_data,
                             http_header=http_header,
                             http_content=b'',
                             client_socket=connection,
                             server=self,
                             **handle.args(request))
        if inspect.isasyncgenfunction(handle.function):
            async for response in cor:
                buffer = utils.optional(response.make, version=request.version, type=request.version, htrf=self.htrf)
                packages = [buffer[x:x + self.max_bytes_per_receive] for x in
                            range(0, len(buffer), self.max_bytes_per_receive)]
                i = 0
                while i < len(packages):
                    try:
                        await connection.send(packages[i])
                        i += 1
                    except TimeoutError:
                        continue
            await request.body.skip()
            return True
        response = await cor
        if type(response) is int:
            handle = self.hcdp[response]
            if handle:
                return await self.answer_request(connection, handle, request, http_data, http_header, max_requests)
            self.logger.error(f'Error code {response} `s handler is not defined')
        elif response:
            buffer = utils.optional(response.make, version=request.version, type=request.version, htrf=self.htrf)
            packages = [buffer[x:x + self.max_bytes_per_receive] for x in
                        range(0, len(buffer), self.max_bytes_per_receive)]
            i = 0
            while i < len(packages):
                try:
                    await connection.send(packages[i])
                    i += 1
                except TimeoutError:
                    continue
        await request.body.skip()
        return True
