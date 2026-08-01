from typing import Protocol


class FilterProtocol(Protocol):
    def size(self, *args, **kwargs) -> int: ...

    def args(self, *args, **kwargs) -> dict: ...
