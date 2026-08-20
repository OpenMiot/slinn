from slinn.net.http import HttpHeaders
from slinn.net.http.responses import HttpResponse
import hashlib
import base64


class WebSocketHandshake(HttpResponse):
    _STATIC_GUID = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def __init__(self, sec_websocket_key: str):
        sec_websocket_accept = base64.b64encode(hashlib.sha1(
            sec_websocket_key.encode()+WebSocketHandshake._STATIC_GUID
        ).digest()).decode()
        
        super().__init__(
            headers = HttpHeaders(default_headers = {
                'Upgrade': ('websocket', ),
                'Connection': ('Upgrade', ),
                'Sec-WebSocket-Accept': (sec_websocket_accept, )
            }),
            status = '101 Switching Protocols',
            body_mixin = False
        )
