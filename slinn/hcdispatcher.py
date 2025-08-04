from .exceptions import HandlerNotFound


class HCDispatcher:

    """
    Class for handling HTTP-codes
    """

    def __init__(self) -> None:
        self.functions = {}

    def __getitem__(self, key: int) -> callable:
        if str(key) in self.functions.keys():
            return self.functions[str(key)]
        raise HandlerNotFound(f'HTTP-code {key} does not exist')

    def __call__(self, code: int) -> callable:
        if code < 99 or code > 599:
            raise HandlerNotFound(f'HTTP-code {code} does not correct')

        def wrapper(func):
            self.functions[str(code)] = func
            return func

        return wrapper
