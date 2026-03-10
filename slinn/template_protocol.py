from typing import Protocol, runtime_checkable


@runtime_checkable
class TemplateProtocol(Protocol):
    @staticmethod
    def install(path: str): ...
