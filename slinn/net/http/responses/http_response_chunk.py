from typing import Any
from slinn.net.http import HttpRequest
from slinn import utils


class HttpResponseChunk:
    def __init__(self, payload: Any) -> None:
        self.payload = utils.representate(payload)

    def make(self, request: HttpRequest) -> bytes:
        return self.payload
