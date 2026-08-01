from . import HttpResponseHeader


class HttpRedirect(HttpResponseHeader):

    """
    Class for redirect to specified location
    """
    
    def __init__(
        self,
        location: str
    ):
        HttpResponseHeader.__init__(self, [('Location', location)], status='307 Temporary Redirect')
