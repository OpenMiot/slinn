from . import Request, utils
import asyncio


class AsyncRequest(Request):
    """
    Representation of HTTP request from client
    """

    def __init__(self, loop, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.loop = loop

    async def respond(self, response_class, *args, **kwargs) -> None:
        buffer = utils.optional(response_class(*args, **kwargs).make, version = self.version, htrf = self.htrf)
        if buffer is None:
            return
        packages = [buffer[x:x + self.server.max_bytes_per_receive] for x in
                    range(0, len(buffer), self.server.max_bytes_per_receive)]
        i = 0
        while i < len(packages):
            try:
                await self.connection.send(packages[i])
                i += 1
            except TimeoutError:
                continue

    async def recv(self, n_bytes: int) -> bytes:
        return await self.loop.sock_recv(self.connection, n_bytes)
