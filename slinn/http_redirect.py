from . import HttpResponse


class HttpRedirect(HttpResponse):

    """
    Class for redirect to specified location
    """
    
    def __init__(self, location: str) -> None:
        HttpResponse.__init__(self, '', [('Location', location)], status='307 Temporary Redirect')
