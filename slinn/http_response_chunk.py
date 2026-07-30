from . import TCPResponseChunk


class HttpResponseChunk(TCPResponseChunk):
    def make(self, version: str = 'HTTP/1.1') -> bytes:
        return self.payload
