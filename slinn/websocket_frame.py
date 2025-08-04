from __future__ import annotations
from . import WebSocketOpcodes
import asyncio


class WebSocketFrame:
    def __init__(self, final: bool, opcode: WebSocketOpcodes, mask: bool, payload: bytes, masking_key: bytes = None) -> None:
        self.final = final
        self.opcode = opcode
        self.mask = mask
        self.masking_key = masking_key
        self.payload = payload

    @staticmethod
    def mask_payload(payload: bytes, masking_key: bytes):
        for i, byte in enumerate(payload):
            yield byte ^ masking_key[i % len(masking_key)]

    @staticmethod
    def pack(frame: WebSocketFrame):
        data = bytearray(b'\0'*2)

        ### +-+-+-+-+-------+
        ### |F|R|R|R| opcode|
        ### |I|S|S|S|  (4)  |
        ### |N|V|V|V|       |
        ### | |1|2|3|       |
        ### +-+-+-+-+-------+
        data[0] |= frame.final << 7
        data[0] |= frame.opcode.value

        ### +-+-------------+
        ### |M| Payload len |
        ### |A|     (7)     |
        ### |S|             |
        ### |K|             |
        ### +-+-------------+
        data[1] |= frame.mask << 7
        data[1] |= len(frame.payload) if len(frame.payload) < 126 else (126 if len(frame.payload) < 65536 else 127)

        ### +-------------------------------+
        ### |    Extended payload length    |
        ### |             (16/64)           |
        ### |   (if payload len == 126/127) |
        ### +-------------------------------+
        if 125 < len(frame.payload) < 65536:
            data += len(frame.payload).to_bytes(length=2, byteorder='big')
        elif 65535 < len(frame.payload):
            data += len(frame.payload).to_bytes(length=4, byteorder='big')

        ### +-------------------------------+
        ### |Masking-key, if MASK set to 1  |
        ### +-------------------------------+
        if frame.mask:
            data += frame.masking_key

        ### +-------------------------------+
        ### |          Payload Data         |
        ### +-------------------------------+
        if frame.mask:
            masked_payload = bytearray(len(frame.payload))
            for i, c in enumerate(WebSocketFrame.mask_payload(frame.payload, frame.masking_key)):
                masked_payload[i] = c
            data += bytes(masked_payload)
        else:
            data += frame.payload

        return bytes(data)

    @staticmethod
    def unpack(data: bytes):
        frame = WebSocketFrame(True, WebSocketOpcodes.CLOSE, False, b'')

        frame.final = bool(data[0] & 128)
        frame.opcode = WebSocketOpcodes(data[0] & 15)

        frame.mask = bool(data[1] & 128)
        payload_len = data[1] & 127

        i = 2
        if payload_len == 126:
            payload_len = data[2:4]
            i += 2
        elif payload_len == 127:
            payload_len = data[2:6]
            i += 4

        if frame.mask:
            frame.masking_key = data[i:i + 4]
            i += 4
            frame.payload = bytearray(payload_len)
            for i, c in enumerate(WebSocketFrame.mask_payload(data[i:i + payload_len], frame.masking_key)):
                frame.payload[i] = c
            frame.payload = bytes(frame.payload)
        else:
            frame.payload = data[i:i + payload_len]

        return frame

    @staticmethod
    async def _sock_read(recv):
        data = bytearray(recv(2))
        payload_len = data[1] & 127
        if payload_len == 126:
            data += recv(2)
            payload_len = data[2:4]
        elif payload_len == 127:
            data += recv(4)
            payload_len = data[2:6]
        if data[1] & 128:
            data += recv(4)
        if payload_len < 126:
            data += recv(payload_len)
        elif 125 < payload_len < 65536:
            data += recv(payload_len)
        else:
            data += recv(payload_len)
        return WebSocketFrame.unpack(data)

    @staticmethod
    def sock_read(sock):
        data = bytearray(sock.recv(2))
        payload_len = data[1] & 127
        if payload_len == 126:
            data += sock.recv(2)
            payload_len = data[2:4]
        elif payload_len == 127:
            data += sock.recv(4)
            payload_len = data[2:6]
        if data[1] & 128:
            data += sock.recv(4)
        if payload_len < 126:
            data += sock.recv(payload_len)
        elif 125 < payload_len < 65536:
            data += sock.recv(payload_len)
        else:
            data += sock.recv(payload_len)
        return WebSocketFrame.unpack(data)

    @staticmethod
    async def _async_sock_read(recv):
        data = bytearray(await recv(2))
        payload_len = data[1] & 127
        if payload_len == 126:
            data += await recv(2)
            payload_len = data[2:4]
        elif payload_len == 127:
            data += await recv(4)
            payload_len = data[2:6]
        if data[1] & 128:
            data += await recv(4)
        if payload_len < 126:
            data += await recv(payload_len)
        elif 125 < payload_len < 65536:
            data += await recv(payload_len)
        else:
            data += await recv(payload_len)
        return WebSocketFrame.unpack(data)

    @staticmethod
    async def async_sock_read(sock):
        loop = asyncio.get_running_loop()
        data = bytearray(await loop.sock_recv(sock, 2))
        payload_len = data[1] & 127
        if payload_len == 126:
            data += await loop.sock_recv(sock, 2)
            payload_len = data[2:4]
        elif payload_len == 127:
            data += await loop.sock_recv(sock, 4)
            payload_len = data[2:6]
        if data[1] & 128:
            data += await loop.sock_recv(sock, 4)
        if payload_len < 126:
            data += await loop.sock_recv(sock, payload_len)
        elif 125 < payload_len < 65536:
            data += await loop.sock_recv(sock, payload_len)
        else:
            data += await loop.sock_recv(sock, payload_len)
        return WebSocketFrame.unpack(data)


if __name__ == '__main__':
    frame = WebSocketFrame(True, WebSocketOpcodes.TEXT, True, b'Hello', b'\x37\xfa\x21\x3d', )
    data = WebSocketFrame.pack(frame)
    print(' '.join(byte.to_bytes(length=1, byteorder='big').hex() for byte in data))
    print(WebSocketFrame.unpack(data).__dict__)
