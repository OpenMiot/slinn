from typing import Protocol, runtime_checkable


@runtime_checkable
class TemplateProtocol(Protocol):
    @staticmethod
    def install(app_path: str, template_path: str): ...
