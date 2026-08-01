from .i_path import IPath


class Path(IPath):
    def __init__(self, pattern: str, methods: tuple[str, ...] = ('GET', 'POST')):
        super().__init__(r'^\/?' + pattern.replace('/', r'\/'), methods)
