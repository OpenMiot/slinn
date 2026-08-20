from typing import Any
from slinn.net.http import HttpHeaders
from slinn import utils


class HttpBodyMixin:
    def __init__(self, payload: Any) -> None:
        self.payload = utils.representate(payload)

    async def make(self, *, chunked: bool, **kwargs) -> bytes:
        if not hasattr(self, 'payload'):
            return b''
        if self.payload and chunked: 
            return b''.join((hex(len(self.payload))[2:].upper().encode(), b'\r\n', self.payload, b'\r\n'))
        else:
            return self.payload
