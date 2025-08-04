from . import utils
from typing import Any

class TCPResponseChunk:
    def __init__(self, payload: Any) -> None:
        self.payload = utils.representate(payload)

    def make(self) -> bytes:
        return self.payload
