from typing import Any
from slinn.net.http import HttpHeaders
from slinn import utils


class HttpChunkResponse:
    def __init__(self, payload: Any) -> None:
        self.payload = utils.representate(payload)

    def make(self, headers: HttpHeaders) -> bytes:
        return self.payload
