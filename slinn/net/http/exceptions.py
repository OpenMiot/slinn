from slinn.exceptions import ProtocolError
from slinn.utils import wrap_in_quotes
from slinn import _


class HttpProtocolError(ProtocolError): ...
class PseudoHeaderIsNotProvided(HttpProtocolError):
    def __init__(self, name):
        super().__init__(_('pseudo-header {name} is not provided').format(name = wrap_in_quotes(name)))

class HttpHeaderAlreadySent(HttpProtocolError):
    def __init__(self):
            super().__init__(_('http header has already sent'))
