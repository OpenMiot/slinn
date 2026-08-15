from . import HttpChunkResponse
from slinn.net.http import HttpHeaders, HttpVersion
from typing import Any
import slinn
import enum
import datetime


class CookieSameSite(enum.Enum):
    STRICT = 0
    LAX = 1
    NONE = 2


class HttpHeaderResponse(HttpChunkResponse):
    def __init__(
        self,
        headers: HttpHeaders | None = None,
        status: str = '200 OK',
        content_type: str = 'text/plain; charset=utf-8',
    ):
        HttpChunkResponse.__init__(self, '')
        self.headers = headers or HttpHeaders()
        self.headers.add_many({
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
    ) -> HttpChunkResponse:
        attributes = attributes or {}
        attributes.update({
            'Domain': domain,
            'Expires': expires.strftime('%a, %d %b %Y %H:%M:%S GMT') if expires else None,
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

    def make_headers(self, recv_headers: HttpHeaders) -> bytes:
        self.headers.version = recv_headers.version
        self.headers.set(
            'Connection',
            recv_headers.get('Connection', 'close' if recv_headers.version is HttpVersion.H1 else 'Keep-Alive')
        )
        return self.headers.make()
