from __future__ import annotations
from typing import Optional, Iterator, Callable
from . import WebSocketOpcodes
import asyncio


class WebSocketFrame:
    def __init__(
        self,
        final: bool,
        opcode: WebSocketOpcodes,
        mask: bool,
        payload: bytes,
        masking_key: Optional[bytes] = None
    ):
        self.final = final
        self.opcode = opcode
        self.mask = mask
        self.masking_key = masking_key
        self.payload = payload

    @staticmethod
    def mask_payload(payload: bytes, masking_key: bytes) -> Iterator[int]:
        for i, byte in enumerate(payload):
            yield byte ^ masking_key[i % len(masking_key)]

    @staticmethod
    def pack(frame: WebSocketFrame) -> bytes:
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
    def unpack(data: bytes) -> WebSocketFrame:
        frame = WebSocketFrame(True, WebSocketOpcodes.CLOSE, False, b'')

        frame.final = bool(data[0] & 128)
        frame.opcode = WebSocketOpcodes(data[0] & 15)

        frame.mask = bool(data[1] & 128)
        payload_len = data[1] & 127

        i = 2
        if payload_len == 126:
            payload_len = int.from_bytes(data[2:4])
            i += 2
        elif payload_len == 127:
            payload_len = int.from_bytes(data[2:6])
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


if __name__ == '__main__':
    frame = WebSocketFrame(True, WebSocketOpcodes.TEXT, True, b'Hello', b'\x37\xfa\x21\x3d', )
    data = WebSocketFrame.pack(frame)
    print(' '.join(byte.to_bytes(length=1, byteorder='big').hex() for byte in data))
    print(WebSocketFrame.unpack(data).__dict__)
