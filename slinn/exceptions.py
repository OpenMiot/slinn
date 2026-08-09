# Exceptions
class EndpointNotFound(LookupError): pass
class SSEEventIsEmpty(ValueError): pass
class ProtocolError(Exception): pass
class NotAWebSocketConnection(ProtocolError): pass
class PatternDoesNotMatch(ValueError): pass
class SocketClosed(BrokenPipeError): pass
class AppHasNoName(ValueError): pass

class SlinnApiException(Exception): ...

class AppExistsException(SlinnApiException):
    def __init__(self, app_name):
        super().__init__(f'app named \'{app_name}\' exists')

class AppNotExistException(SlinnApiException):
    def __init__(self, app_name):
        super().__init__(f'app named \'{app_name}\' does not exist')

# Warnings
class Endpoint404NotFound(UserWarning): pass
class Endpoint500NotFound(UserWarning): pass
class IncompatibleVersion(UserWarning): pass
