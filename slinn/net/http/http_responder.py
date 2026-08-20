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
        if not endpoint.is_generator:
            resp_headers = await self.answer_response(await coro, request, args, resp_headers, extend_headers)
        else:
            async for response in coro:
                resp_headers = await self.answer_response(response, request, args, resp_headers, extend_headers)
        t1 = loop.time()
        if skip_body:
            await request.body.skip()
        t2 = loop.time()
        if trail and resp_headers and 'chunked' in resp_headers.get('Transfer-Encoding', '').lower():
            await self.client_pipe.send(b'0\r\n')
            if 'server-timing' in resp_headers.get('Trailer', '').lower():
                await self.client_pipe.send(
                    (
                        'Server-Timing: '
                        f'endpoint;desc="Making response";dur={(t1-t0)*1000},'
                        f'skip;desc="Body skip";dur={(t2-t1)*1000}\r\n'
                    ).encode()
                )
            await self.client_pipe.send(b'\r\n')
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
    ) -> HttpHeaders:
        if not response:
            return
        if isinstance(response, int):
            return await self.handle_endpoint(self.http_codes_router[response], request, args, extend_headers)
        if not isinstance(response, HttpBodyMixin) and not isinstance(response, HttpHeadersMixin):
            response = HttpResponse(response)
        if isinstance(response, HttpHeadersMixin) and not resp_headers:
            resp_headers = extend_headers
            if args['request'].headers.version == HttpVersion.H11:
                resp_headers.add_many({
                    'Trailer': ('Server-Timing', ),
                    'Transfer-Encoding': ('chunked', )
                })
            response.headers.extend(resp_headers)
            await self.client_pipe.send(
                await response.make(
                    HttpHeadersMixin,
                    request = args['request'],
                    ft_router = self.file_types_router
                )
            )
        await self.client_pipe.send(await response.make(
            HttpBodyMixin,
            chunked = resp_headers and 'chunked' in resp_headers.get('Transfer-Encoding', '')
        ))
        return resp_headers
