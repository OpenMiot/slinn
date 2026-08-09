from .exceptions import EndpointNotFound
from slinn.net import Endpoint
from slinn.net.http.filters import AnyFilter
from typing import Callable


class HCDispatcher:

    """
    Class for handling HTTP-codes
    """

    def __init__(self) -> None:
        self.functions = {}

    def __getitem__(self, key: int) -> Endpoint:
        if str(key) in self.functions.keys():
            return Endpoint(AnyFilter, self.functions[str(key)])
        raise EndpointNotFound(f'HTTP-code {key} does not exist')

    def __call__(self, code: int) -> Callable[[Callable], Callable]:
        if code < 99 or code > 599:
            raise EndpointNotFound(f'HTTP-code {code} does not correct')

        def wrapper(func):
            self.functions[str(code)] = func
            return func

        return wrapper
