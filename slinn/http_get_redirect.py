from . import HttpResponseHeader


class HttpGETRedirect(HttpResponseHeader):
    """
    Class for redirect to specified location
    """

    def __init__(self, location: str) -> None:
        HttpResponseHeader.__init__(self, data=[('Location', location)], status='303 See Other')
