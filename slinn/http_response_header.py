from . import HttpResponseChunk
import slinn
import enum
import datetime


class CookieSameSite(enum.Enum):
    STRICT = 0
    LAX = 1
    NONE = 2


class HttpResponseHeader(HttpResponseChunk):
    def __init__(self, data: list[tuple] = None, status: str = '200 OK',
                 content_type: str = 'text/plain; charset=utf-8', use_gzip: bool=True) -> None:
        HttpResponseChunk.__init__(self, '')
        self.data = ([
                        ('Content-Type', content_type),
                        ('Server', slinn.version),
                        ('Connection', 'Keep-Alive'),
                    ] + (data if data is not None else []))
        self.status = status
        self.use_gzip=use_gzip

    def set_cookie(self,
                   key: str,
                   value: any,
                   domain: str = None,
                   expires: datetime.datetime = None,
                   http_only: bool = None,
                   max_age: int = None,
                   partitioned: bool = None,
                   path: str = None,
                   secure: bool = None,
                   same_site: CookieSameSite = None,
                   attributes: dict = None) -> None:
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

    def make(self, version: str = 'HTTP/1.1') -> bytes:
        self.payload = (f'{version} {self.status}' + '\r\n'
                       + "\r\n".join([
                           str(dat[0]) + ": " + str(dat[1])
                           for dat in self.data + ([('Content-Encoding', 'gzip')] if self.use_gzip else [])
                       ]) + '\r\n\r\n').encode('utf-8') + self.payload
        return super().make(version)
