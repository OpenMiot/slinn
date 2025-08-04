from abc import ABC, abstractmethod


class IMiddleware(ABC):

    """
    Interface for creating middlewares
    """

    def __init__(self, *args, **kwargs) -> None: ...
    
    @abstractmethod
    def __call__(self, *args, **kwargs) -> callable: ...
