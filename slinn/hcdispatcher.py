from .exceptions import HandlerNotFound
from . import Handle, AnyFilter
from typing import Callable


class HCDispatcher:

    """
    Class for handling HTTP-codes
    """

    def __init__(self) -> None:
        self.functions = {}

    def __getitem__(self, key: int) -> Handle:
        if str(key) in self.functions.keys():
            return Handle(AnyFilter, self.functions[str(key)])
        raise HandlerNotFound(f'HTTP-code {key} does not exist')

    def __call__(self, code: int) -> Callable[[Callable], Callable]:
        if code < 99 or code > 599:
            raise HandlerNotFound(f'HTTP-code {code} does not correct')

        def wrapper(func):
            self.functions[str(code)] = func
            return func

        return wrapper
