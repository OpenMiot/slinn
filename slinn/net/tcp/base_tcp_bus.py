from slinn.eda import BaseBus, on
from slinn.net.tcp import TcpPipe
from slinn.net.tcp.events import DataReceived, Accepted
from slinn.net.address import Address


class BaseTcpBus(BaseBus):
    def __init__(self):
        super().__init__()
    
    @on(Accepted)
    async def on_accepted(self):
        ...
    
    @on(DataReceived)
    async def on_data_received(self, data: bytes, client_pipe: TcpPipe, client_address: Address):
        ...
