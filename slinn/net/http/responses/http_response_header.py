from . import HttpResponseChunk
from typing import Optional, Any
import slinn
import enum
import datetime


class CookieSameSite(enum.Enum):
    STRICT = 0
    LAX = 1
    NONE = 2


class HttpResponseHeader(HttpResponseChunk):
    def __init__(
        self,
        data: Optional[list[tuple]] = None,
        status: str = '200 OK',
        content_type: str = 'text/plain; charset=utf-8',
        use_gzip: bool = True
    ):
        HttpResponseChunk.__init__(self, '')
        self.data = ([
                        ('Content-Type', content_type),
                        ('Server', slinn.version),
                        ('Connection', 'Keep-Alive'),
                    ] + (data if data is not None else []))
        self.status = status
        self.use_gzip = use_gzip

    def set_cookie(
        self,
        key: str,
        value: Any,
        domain: Optional[str] = None,
        expires: Optional[datetime.datetime] = None,
        http_only: Optional[bool] = None,
        max_age: Optional[int] = None,
        partitioned: Optional[bool] = None,
        path: Optional[str] = None,
        secure: Optional[bool] = None,
        same_site: Optional[CookieSameSite] = None,
        attributes: Optional[dict] = None
    ) -> HttpResponseChunk:
        if attributes is None:
            attributes = {}
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
        self.data.append((
            'Set-Cookie',
            f'{key}={value}' +
            ''.join([
                f'; {key}' + ('' if type(attributes[key]) is bool else f'={attributes[key]}')
                for key in attributes.keys()
            ])
        ))
        return self

    def make(self, version: str = 'HTTP/1.1') -> bytes:
        self.payload = (f'{version} {self.status}' + '\r\n'
                       + "\r\n".join([
                           str(dat[0]) + ": " + str(dat[1])
                           for dat in self.data + ([('Content-Encoding', 'gzip')] if self.use_gzip else [])
                       ]) + '\r\n\r\n').encode('utf-8') + self.payload
        return super().make(version)
