from typing import Protocol


class ResponseProtocol(Protocol):
    def make(self, *args, **kwargs) -> bytes: ...
