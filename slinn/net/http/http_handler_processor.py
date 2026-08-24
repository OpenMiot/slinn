from slinn.net.http import HCRouter
from slinn.net.http.responses import HttpResponse
from slinn.utils import optional
from typing import Any
from collections.abc import Callable, AsyncGenerator
import inspect


class HttpHandlerProcessor:
    @staticmethod
    async def process(handler: Callable, is_generator: bool | None = None, **kwargs):
        async def _process_response(response: Any) -> AsyncGenerator[HttpResponse]:
            if isinstance(response, HttpResponse):
                yield response
            elif isinstance(response, int):
                endpoint = kwargs['http_codes_router'][response]
                async for chunk in HttpHandlerProcessor.process(
                    endpoint.handler,
                    is_generator = endpoint.is_generator,
                    **kwargs
                ):
                    yield chunk
            else:
                yield HttpResponse(response)
        
        coro = optional(handler, **kwargs)
        if is_generator or (is_generator is None and inspect.isasyncgenfunction(handler)):
            async for response in coro:
                async for chunk in _process_response(response):
                    yield chunk
        else:
            async for chunk in _process_response(await coro):
                yield chunk
