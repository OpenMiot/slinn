from abc import ABC, abstractmethod


class Migration(ABC):
    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    @abstractmethod
    async def check(self) -> bool: ...

    @abstractmethod
    async def apply(self) -> None: ...
