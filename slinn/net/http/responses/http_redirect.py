from . import HttpHeaderResponse


class HttpRedirect(HttpHeaderResponse):

    """
    Class for redirect to specified location
    """
    
    def __init__(
        self,
        location: str
    ):
        HttpHeaderResponse.__init__(self, [('Location', location)], status='307 Temporary Redirect')
