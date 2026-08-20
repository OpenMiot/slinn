from slinn.net.http import HttpHeaders, HttpVersion, HttpRequest
from typing import Any
import slinn
import enum
import datetime


class CookieSameSite(enum.Enum):
    STRICT = 0
    LAX = 1
    NONE = 2


class HttpHeadersMixin:
    def __init__(
        self,
        headers: HttpHeaders | None = None,
        status: str = '200 OK',
        content_type: str = 'text/plain; charset=utf-8',
    ):
        self.headers = headers or HttpHeaders()
        self.headers.set_many({
            'Content-Type': (content_type, ),
            'Server': (slinn.version, ),
            ':status': (status, )
        })
        

    def set_cookie(
        self,
        key: str,
        value: Any,
        *,
        domain: str | None = None,
        expires: datetime.datetime | None = None,
        http_only: bool | None = None,
        max_age: int | None = None,
        partitioned: bool | None = None,
        path: str | None = None,
        secure: bool | None = None,
        same_site: CookieSameSite | None = None,
        attributes: dict | None = None
    ) -> HttpHeadersMixin:
        attributes = attributes or {}
        attributes.update({
            'Domain': domain,
            'Expires': slinn.utils.convert_datetime(expires) if expires else None,
            'HttpOnly': http_only,
            'Max-Age': max_age,
            'Partitioned': partitioned,
            'Path': path,
            'Secure': secure,
            'SameSite': same_site.name.capitalize() if same_site else None
        })
        for _key, _value in attributes.copy().items():
            if _value is None:
                del attributes[_key]
        self.headers.add(
            'Set-Cookie',
            f'{key}={value}' +
            ''.join([
                f'; {key}' + ('' if type(attributes[key]) is bool else f'={attributes[key]}')
                for key in attributes
            ])
        )
        return self

    async def make(self, *, recv_headers: HttpRequest, **kwargs) -> bytes:
        self.headers.version = recv_headers.version
        self.headers.set(
            'Connection',
            recv_headers.get('Connection', 'close' if recv_headers.version == HttpVersion.H1 else 'Keep-Alive')
        )
        self.headers.set(
            'Date',
            slinn.utils.convert_datetime(datetime.datetime.now(datetime.UTC))
        )
        if hasattr(self, 'payload') and 'chunked' not in self.headers.get('Transfer-Encoding', ''):
            self.headers.set('Content-Length', len(self.payload))
        return self.headers.make()
