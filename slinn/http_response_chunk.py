from . import TCPResponseChunk, utils


class HttpResponseChunk(TCPResponseChunk):
    def make(self, version: str = 'HTTP/1.0', use_gzip: bool = False) -> bytes:
        return self.payload
