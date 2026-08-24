from slinn.net.http import HttpHeaders, HttpVersion, HttpRequest, FTRouter, HCRouter, HttpHandlerProcessor
from slinn.net.http.responses import HttpHeadersMixin, HttpBodyMixin, HttpResponse
from slinn.net.tcp import TcpPipe
from slinn.net import Endpoint
from slinn.utils import optional
from typing import Any
import time


class HttpResponder:
    def __init__(self, client_pipe: TcpPipe, file_types_router: FTRouter | None):
        self.client_pipe = client_pipe
        self.file_types_router = file_types_router or FTRouter()
    
    async def handle_endpoint(
        self,
        endpoint: Endpoint,
        request: HttpRequest,
        args: frozendict,
        extend_headers: HttpHeaders,
        skip_body = False,
        trail = False,
        may_close = False
    ) -> HttpHeaders:
        t0 = time.perf_counter_ns()
        resp_headers: HttpHeaders | None = None
        ignore_body = hasattr(endpoint.handler, 'ignore_body') and endpoint.handler.ignore_body
        bytes_resp = bytearray()
        async for chunk in HttpHandlerProcessor.process(
            endpoint.handler,
            is_generator = endpoint.is_generator,
            **args
        ):
            if bytes_resp:
                await self.client_pipe.send(bytes_resp)
            bytes_resp, resp_headers = await self.answer_response(
                chunk,
                args,
                resp_headers,
                extend_headers,
                ignore_body = ignore_body
            )
        t1 = time.perf_counter_ns()
        if skip_body:
            await request.body.skip()
        t2 = time.perf_counter_ns()
        if trail and resp_headers and 'chunked' in resp_headers.get('Transfer-Encoding', '').lower():
            bytes_resp.extend(b'0\r\n')
            if 'server-timing' in resp_headers.get('Trailer', '').lower():
                bytes_resp.extend(
                    (
                        'Server-Timing: '
                        f'endpoint;desc="Making response";dur={(t1-t0)*1e-6},'
                        f'skip;desc="Body skip";dur={(t2-t1)*1e-6}\r\n'
                    ).encode()
                )
            bytes_resp.extend(b'\r\n')
        await self.client_pipe.send(bytes_resp)
        if may_close and request.headers.get(
            'Connection', 'close' if request.headers.version == HttpVersion.H1 else 'Keep-Alive') == 'close':
            self.client_pipe.close()
        return bytearray(), resp_headers

    async def answer_response(
        self,
        response: Any,
        args: frozendict,
        resp_headers: HttpHeaders,
        extend_headers: HttpHeaders,
        ignore_body: bool = False
    ) -> tuple[bytearray, HttpHeaders | None]:
        if not response:
            return bytearray(), None
        bytes_resp = bytearray()
        if isinstance(response, HttpHeadersMixin) and not resp_headers:
            resp_headers = extend_headers
            if args['request'].headers.version == HttpVersion.H11:
                resp_headers.add_many({
                    'Trailer': ('Server-Timing', ),
                    'Transfer-Encoding': ('chunked', )
                })
            response.headers.extend(resp_headers)
            bytes_resp.extend(
                await response.make(
                    HttpHeadersMixin,
                    recv_headers = args['request'].headers,
                    ft_router = self.file_types_router
                )
            )
        if not ignore_body:
            bytes_resp.extend(await response.make(
                HttpBodyMixin,
                chunked = resp_headers and 'chunked' in resp_headers.get('Transfer-Encoding', '')
            ))
        return bytes_resp, resp_headers
