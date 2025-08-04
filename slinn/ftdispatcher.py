from . import Handle


class FTDispatcher:

    """
    Class for handling filetypes
    """
    
    def __init__(self) -> None:
        self.handles = []

    def by_extension(self, extension: str) -> callable:
        def wrapper(func):
            self.handles.append(Handle(r'.*\.' + extension + r'$', func))
            return func

        return wrapper
    
    def by_regexp(self, regexp: str) -> callable:
        def wrapper(func):
            self.handles.append(Handle(regexp, func))
            return func

        return wrapper
