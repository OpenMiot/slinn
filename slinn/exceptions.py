# Exceptions
class EndpointNotFound(LookupError): pass
class SSEEventIsEmpty(ValueError): pass
class ProtocolError(Exception): pass
class NotAWebSocketConnection(ProtocolError): pass
class PatternDoesNotMatch(ValueError): pass
class SocketClosed(BrokenPipeError): pass
class AppHasNoName(ValueError): pass

# Warnings
class Endpoint404NotFound(UserWarning): pass
class Endpoint500NotFound(UserWarning): pass
class IncompatibleVersion(UserWarning): pass
