from slinn import MiddlewareProtocol
from slinn.net.ws import WebSocketConnection
from slinn.net.http import HttpRequest
from slinn.net.tcp import TcpPipe
from slinn.utils import optional


class WebSocketMiddleware(MiddlewareProtocol):
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        
    def __call__(self, func):
        async def wrapper(request: HttpRequest, client_pipe: TcpPipe, *args, **kwargs):
            websocket = WebSocketConnection(request.headers, client_pipe)
            await websocket.handshake()
            websocket.set_timeout(self.timeout)
            return await optional(func, *args, **(kwargs | {
                'request' : request, 'client_pipe': client_pipe, 'websocket': websocket}))
        return wrapper
