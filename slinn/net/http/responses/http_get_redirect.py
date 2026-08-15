from . import HttpHeaderResponse


class HttpGETRedirect(HttpHeaderResponse):
    """
    Class for redirect to specified location
    """

    def __init__(
        self,
        location: str
    ):
        HttpHeaderResponse.__init__(self, data=[('Location', location)], status='303 See Other')
