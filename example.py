from slinn import AsyncServer, HttpResponse, Address, ResponseHeader, ResponseChunk, ApiDispatcher, SSEHeader, SSEEvent, WebSocketHandshake, AsyncWebSocketConnection, WebSocketFrame, WebSocketOpcodes, IMiddleware, Server
from slinn.storage import Storage
from slinn.utils import optional
import logging
import os
import asyncio
import socket


logging.basicConfig(level=logging.INFO)
dp = ApiDispatcher()


class ExampleMiddleware(IMiddleware):
    def __init__(self, lolkek):
        super().__init__()
        self.lolkek = lolkek

    def __call__(self, func):
        print(1)
        async def wrapper(request, http_data, http_header, http_content, connection, server, *args, **kwargs):
            print(2)
            return await optional(func,
                     request=request,
                     http_data=http_data,
                     http_header=http_header,
                     http_content=http_content,
                     client_socket=connection,
                     server=server,
                     *args,
                     **(kwargs|self.__dict__)
            )
        return wrapper


@dp.get()
async def index(request):
    await request.respond(HttpResponse, 'Hello, world')

@dp.get('test')
def test(request):
    request.respond(HttpResponse, 'test')


@dp.get('gpsl')
async def gpsl(request):
    await request.respond(ResponseHeader, [('Content-Length', os.path.getsize(r'C:\Users\mrybs\Downloads\ГПсЛ.zip'))])

    with open(r'C:\Users\mrybs\Downloads\ГПсЛ.zip', 'rb') as f:
        i = 1
        while data := f.read(1024*64):
            await request.respond(ResponseChunk, data)
            await asyncio.sleep(0)
            i += 1


@dp.get('sse')
async def sse(request):
    print('sse')
    await request.respond(SSEHeader, '*')
    while True:
        await request.respond(SSEEvent, full_data=['lolkek'], event_id=1488, retry=500, comments=['alikhan daun eblan'], event='да по жизни так')
        await asyncio.sleep(1)


@dp.get('ws')
async def ws(request):
    conn = AsyncWebSocketConnection(request)
    await conn.handshake()
    while frame := await conn.read():
        if conn.closed:
            break
        await conn.send('you have sent: ' + frame.payload.decode())

@ExampleMiddleware('4eburek')
@dp.get('/user/<int user_id>')
async def path(user_id, lolkek=None):
    return HttpResponse(str(user_id) + str(lolkek))

@dp.post('upload2')
async def upload(request):
    data = bytearray()
    request.connection.settimeout(0.3)
    while len(data) < int(request.header['data'].get('Content-Length', 0)):
        print(data)
        try:
            b = await request.recv(12800)
            data += b
            print(data)
        except (TimeoutError, socket.timeout):
            print('Timed out!')
            break
    print('data:', data)
    print('files:', request.files)
    await request.respond(HttpResponse, data)

@dp.post('upload')
def upload(request):
    data = bytearray()
    while len(data) < int(request.header['data'].get('Content-Length', 0)):
        print(data)
        try:
            b = request.recv(128)
            data += b
            print(data)
        except (TimeoutError, socket.timeout):
            print('Timed out!')
            break
    print('data:', data)
    print('files:', request.files)
    request.respond(HttpResponse, data)


import inspect
print(inspect.signature(path).parameters['kwargs'].kind)

storage = Storage('root')

with storage('index.html', 'w') as file:
    file.write('lol')

print([handle.filter._pattern for handle in dp.handles])
#asyncio.run(AsyncServer(dp, ssl_fullchain='localhost.crt', ssl_key='localhost.key').listen(Address(8080)))
#asyncio.run(AsyncServer(dp, ssl_fullchain='fullchain.pem', ssl_key='privkey.pem').listen(Address(8080)))
#asyncio.run(AsyncServer(dp).listen(Address(8080, host="192.168.50.68")))
#Server(dp, ssl_fullchain='localhost.crt', ssl_key='localhost.key').listen(Address(8080))
Server(dp).listen(Address(8080, host="192.168.50.68"))