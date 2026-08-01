from .filter import Filter


class LinkFilter(Filter):

    """
    Class for filtering requests by link
    """
    
    def __init__(self, _filter: str, methods: tuple[str, ...] = ('GET', 'POST')) -> None:
        super().__init__(
            r'\/?' + _filter.replace('/', r'\/') + r'(\/.*)?',
            methods
        )
