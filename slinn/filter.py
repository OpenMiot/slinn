from . import utils


class Filter:

    """
    Base class for filtering requests
    """
    
    def __init__(self, _filter: str, methods: tuple = ('GET', 'POST')) -> None:
        self.filter = _filter
        self.methods = methods

    def check(self, text: str, method: str) -> bool:
        return utils.rematcheswith(text, self.filter) and method.upper() in self.methods

    def size(self, text: str, method: str) -> int:
        a = utils.min_restartswith_size(text, self.filter) if self.check(text, method) else 2147483647
        b = utils.Bmin_restartswith_size(text, self.filter) if self.check(text, method) else 2147483647
        if not self.check(text, method):
            return -1
        elif a == 2147483647:
            return 0
        else:
            return b

    def args(self, *args, **kwargs):
        return {}
