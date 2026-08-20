from slinn.net.http import HttpHeaders, HttpVersion, HttpRequest, FTRouter, HCRouter
from slinn.net.http.responses import HttpHeadersMixin, HttpBodyMixin, HttpResponse
from slinn.net.tcp import TcpPipe
from slinn.net import Endpoint
from slinn.utils import optional
from typing import Any
import asyncio


class HttpResponder:
    def __init__(self, client_pipe: TcpPipe, file_types_router: FTRouter | None, http_codes_router: HCRouter | None):
        self.client_pipe = client_pipe
        self.file_types_router = file_types_router or FTRouter()
        self.http_codes_router = http_codes_router or HCRouter()
    
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
        loop = asyncio.get_running_loop()
        t0 = loop.time()
        coro = optional(endpoint.function, **args)
        resp_headers: HttpHeaders | None = None
        ignore_body = hasattr(endpoint.function, 'ignore_body') and endpoint.function.ignore_body
        bytes_resp = bytearray()
        if not endpoint.is_generator:
            bytes_resp, resp_headers = await self.answer_response(
                await coro,
                request,
                args,
                resp_headers,
                extend_headers,
                ignore_body = ignore_body
            )
        else:
            async for response in coro:
                if bytes_resp:
                    await self.client_pipe.send(bytes_resp)
                bytes_resp, resp_headers = await self.answer_response(
                    response,
                    request,
                    args,
                    resp_headers,
                    extend_headers,
                    ignore_body = ignore_body
                )
        t1 = loop.time()
        if skip_body:
            await request.body.skip()
        t2 = loop.time()
        if trail and resp_headers and 'chunked' in resp_headers.get('Transfer-Encoding', '').lower():
            bytes_resp.extend(b'0\r\n')
            if 'server-timing' in resp_headers.get('Trailer', '').lower():
                bytes_resp.extend(
                    (
                        'Server-Timing: '
                        f'endpoint;desc="Making response";dur={(t1-t0)*1000},'
                        f'skip;desc="Body skip";dur={(t2-t1)*1000}\r\n'
                    ).encode()
                )
            bytes_resp.extend(b'\r\n')
        await self.client_pipe.send(bytes_resp)
        if may_close and request.headers.get(
            'Connection', 'close' if request.headers.version == HttpVersion.H1 else 'Keep-Alive') == 'close':
            self.client_pipe.close()
        return resp_headers

    async def answer_response(
        self,
        response: Any,
        request: HttpRequest,
        args: frozendict,
        resp_headers: HttpHeaders,
        extend_headers: HttpHeaders,
        ignore_body: bool = False
    ) -> tuple[bytearray, HttpHeaders | None]:
        if not response:
            return bytearray(), None
        if isinstance(response, int):
            return await self.handle_endpoint(self.http_codes_router[response], request, args, extend_headers)
        if not isinstance(response, HttpBodyMixin) and not isinstance(response, HttpHeadersMixin):
            response = HttpResponse(response)
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
