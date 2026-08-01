from typing import Any
from slinn import utils


class HttpResponseChunk:
    def __init__(self, payload: Any) -> None:
        self.payload = utils.representate(payload)

    def make(self, version: str = 'HTTP/1.1') -> bytes:
        return self.payload
