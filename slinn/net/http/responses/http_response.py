from . import HttpHeadersMixin, HttpBodyMixin
from slinn.net.http import HttpHeaders
from slinn.utils import representate
from typing import Any
from collections.abc import Callable, Iterable


class HttpResponse(HttpHeadersMixin, HttpBodyMixin):
    """
    Base class for all HTTP responses
    """

    def __init__(
        self,
        payload: Any = b'',
        headers: HttpHeaders | None = None,
        status: str = '200 OK',
        content_type: str = 'text/plain; charset=utf-8',
        *,
        headers_mixin: bool = True,
        body_mixin: bool = True,
        hooks: dict[Callable, Iterable[type]] | None = None
    ):
        payload = representate(payload)
        
        self.headers_mixin = headers_mixin
        self.body_mixin = body_mixin
        
        if self.headers_mixin:
            HttpHeadersMixin.__init__(
                self,
                headers = headers or HttpHeaders(),
                status = status,
                content_type = content_type
            )
        if self.body_mixin:
            HttpBodyMixin.__init__(self, payload)

        self.hooks = hooks or {}

    async def make(self, mixin: type, **kwargs) -> bytes:
        if isinstance(mixin, HttpBodyMixin) and not self.body_mixin:
            print('lol')
            return b''
        if isinstance(mixin, HttpHeadersMixin) and not self.headers_mixin:
            return b''
        for callback, mixins in self.hooks.items():
            if mixin in mixins:
                kwargs = await callback(self, **kwargs)
        return await mixin.make(self, **kwargs)
