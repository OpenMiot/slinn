from .i_path import IPath


class Path(IPath):
    def __init__(self, pattern, methods=('GET', 'POST')):
        super().__init__(r'^\/?' + pattern.replace('/', r'\/'), methods)
