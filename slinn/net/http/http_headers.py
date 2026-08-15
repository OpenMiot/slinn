from typing import Any, SupportsIndex, Iterable
from slinn.net.http.exceptions import PseudoHeaderIsNotProvided
from slinn.utils import representate
import urllib.parse
import enum

class _HttpVersion(enum.Enum):
    H09 = 'HTTP/0.9'
    H1 = 'HTTP/1.0'
    H11 = 'HTTP/1.1'
    H2 = 'HTTP/2.0'
    H3 = 'HTTP/3.0'


class _HttpProtocol(enum.Enum):
    HTTP = 'HTTP'
    HTTPS = 'HTTPS'


class _HttpHeaders:
    __slots__ = ('_data', 'version')

    @staticmethod
    def _normalize_value(value: Any) -> str:
        return value if isinstance(value, str) else representate(value).decode()

    @staticmethod
    def _normalize_key(key: str) -> str:
        key = key.lower() if key.startswith(':') else key.title()
        if key == 'Host':
            return ':authority'
        return key

    @staticmethod
    def parse(raw_http: bytes) -> _HttpHeaders:
        http = raw_http.split(b'\r\n')
        _method, *_path, _version = http[0].split(b' ')

        headers = _HttpHeaders(
            version = _HttpVersion(_version.decode()),
            default = {
                ':method': _method.decode(),
                ':path': urllib.parse.unquote_plus(b' '.join(_path).decode())
            }
        )

        for header in http[1:-2]:
            key, value = header.split(b':', 1)
            headers.add(key.strip().decode(), value.strip().decode())

        return headers

    def __init__(self, *, version: _HttpVersion = _HttpVersion.H11, default: str | None = None):
        self._data: dict[str, list[str]] = {}

        self.version: _HttpVersion = version
        if default:
            for key, value in default.items():
                self.add(key, value)

    @property
    def method(self) -> str | None:
        return self.get(':method').upper()

    @property
    def scheme(self) -> str | None:
        return self.get(':scheme')

    @property
    def authority(self) -> str | None:
        return self.get(':authority')

    @property
    def path(self) -> str | None:
        return self.get(':path')

    @property
    def protocol(self) -> _HttpProtocol | None:
        _protocol = self.get(':protocol')
        return _HttpProtocol(_protocol) if _protocol in _HttpProtocol else None

    @property
    def status(self) -> str | None:
        return self.get(':status')

    def get(self, key: str, default: Any = None) -> str:
        values = self.values(key, [default])
        return values[0] if values else default

    def values(self, key: str, default: Iterable[Any] | None = None) -> Iterable[str]:
        return self._data.get(_HttpHeaders._normalize_key(key), [_HttpHeaders._normalize_value(v) for v in default or []])

    def add(self, key: str, value: Any) -> _HttpHeaders:
        key = _HttpHeaders._normalize_key(key)
        value = _HttpHeaders._normalize_value(value)
        if key in self._data and isinstance(self._data[key], list):
            self._data[key].append(value)
        else:
            self._data[key] = [value]
        return self

    def set(self, key: str, value: Any) -> _HttpHeaders:
        self._data[_HttpHeaders._normalize_key(key)] = [_HttpHeaders._normalize_value(value)]
        return self

    def delete(self, key: str) -> _HttpHeaders:
        del self._data[_HttpHeaders._normalize_key(key)]
        return self

    def pop(self, key: str, index: SupportsIndex = -1) -> str:
        return self._data[_HttpHeaders._normalize_key(key)].pop(index)

    def keys(self):
        return self._data.keys()

    def __contains__(self, key: str):
        return _HttpHeaders._normalize_key(key) in self.keys()

    def make(self):
        if self.status is None:
            raise PseudoHeaderIsNotProvided(':status')
        http: list[bytes] = []
        http.extend((self.version.value.encode(), b' ', self.status.encode() + b'\r\n'))
        for key in self.keys():
            if key.startswith(':'):
                continue
            for value in self.values(key):
                http.extend((key.encode(), b': ', value.encode(), b'\r\n'))
        http.append(b'\r\n')
        return b''.join(http)


from slinn_cxx import HttpHeaders, HttpVersion, HttpProtocol

#HttpHeaders = _HttpHeaders
#HttpVersion = _HttpVersion
#HttpProtocol = _HttpProtocol

if __name__ == '__main__':
    import time
    count = 500000

    _start = time.time()
    for i in range(500000):
        HttpHeaders.parse(b"GET / HTTP/1.1\r\nHost: miot.su\r\n\r\n")
    print(f'C++ parsing {count} times', time.time() - _start)

    _start = time.time()
    for i in range(500000):
        _HttpHeaders.parse(b"GET / HTTP/1.1\r\nHost: miot.su\r\n\r\n")
    print(f'Python parsing {count} times', time.time() - _start)

    headers = HttpHeaders()
    headers.set(':status', '200 OK')
    headers.set('Server', 'Slinn')
    _start = time.time()
    for i in range(500000):
        headers.make()
    print(f'C++ making {count} times', time.time() - _start)

    _headers = _HttpHeaders()
    _headers.set(':status', '200 OK')
    _headers.set('Server', 'Slinn')
    _start = time.time()
    for i in range(500000):
        _headers.make()
    print(f'Python making {count} times', time.time() - _start)

