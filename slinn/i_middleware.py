from abc import ABC, abstractmethod
from typing import Callable


class IMiddleware(ABC):

    """
    Interface for creating middlewares
    """

    @abstractmethod
    def __init__(self, *args, **kwargs): ...
    
    @abstractmethod
    def __call__(self, func: Callable) -> Callable: ...
