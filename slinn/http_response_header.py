from . import HttpResponseChunk
import slinn


class HttpResponseHeader(HttpResponseChunk):
    def __init__(self, data: list[tuple] = None, status: str = '200 OK',
                 content_type: str = 'text/plain; charset=utf-8') -> None:
        HttpResponseChunk.__init__(self, '')
        self.data = [('Content-Type', content_type), ('Server', slinn.version)] + (data if data is not None else [])
        self.status = status

    def set_cookie(self, key: str, value: any, attributes: dict = None) -> None:
        if attributes is None:
            attributes = {}
        self.data.append(('Set-Cookie', f'{key}={value}' +
                         ''.join(
                             [f'; {key}' + ('' if type(attributes[key]) is bool else f'={attributes[key]}') for key in
                              attributes.keys()])))

    def make(self, version: str = 'HTTP/1.0', use_gzip: bool = False) -> bytes:
        self.payload = (f'{version} {self.status}' + '\r\n'
                       + "\r\n".join([
                           str(dat[0]) + ": " + str(dat[1])
                           for dat in self.data + ([('Content-Encoding', 'gzip')] if use_gzip else [])
                       ]) + '\r\n\r\n').encode('utf-8') + self.payload
        return super().make(version, use_gzip)
