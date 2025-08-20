# Exceptions
class HandlerNotFound(LookupError): pass
class SSEEventIsEmpty(ValueError): pass
class ProtocolError(Exception): pass
class NotAWebSocketConnection(ProtocolError): pass
class PatternDoesNotMatch(ValueError): pass

# Warnings
class Handler404NotFound(UserWarning): pass
class Handler500NotFound(UserWarning): pass