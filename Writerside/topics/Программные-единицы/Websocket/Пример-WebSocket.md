# Пример WebSocket

В `app.py` приложения (или где прописан диспатчер):
```Python
from slinn import (
    ApiDispatcher, AsyncRequest, WebSocketOpcodes, AsyncWebSocketGroup
)


dp = ApiDispatcher()
ws_group = AsyncWebSocketGroup()


@dp.get('/ws')
async def websocket_handler(request: AsyncRequest) -> None:
    # Инициализация WebSocket-подключения с таймаутом 60 секунд
    ws = await request.WebSocket(60)

    # Добавление WebSocket-подключения в группу
    ws_group.add(ws)

    while True:
        # Чтение следующего WebSocket-фрейма
        frame = await ws.read()

        # Ответ на пинг - понг
        if frame.opcode == WebSocketOpcodes.PING:
            await ws.pong()
            continue

        # Выход из цикла (соединение само закроется)
        if frame.opcode == WebSocketOpcodes.CLOSE:
            break

        # Отправка полезной нагрузки всем подключенным клиентам кроме
        # отправителя (в группе `ws_group`)
        await ws_group.send(
            frame.payload if frame.opcode == WebSocketOpcodes.BINARY
            else frame.payload.decode(),
            exclude=(ws,)
        )
```