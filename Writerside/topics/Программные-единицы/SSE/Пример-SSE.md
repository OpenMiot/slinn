# Пример SSE

В `app.py` приложения (или где прописан диспатчер):
```Python
from slinn import ApiDispatcher, AsyncRequest, SSEHeader, SSEEvent
from datetime import datetime
import asyncio


dp = ApiDispatcher()


@dp.get('/sse/time')
async def sse_time(request: AsyncRequest):
    # Отправка SSE-заголовка
    await request.respond(SSEHeader)

    while not request.connection.closed():
        # Отправка события с текущим временем каждую секунду
        yield SSEEvent(full_data=(datetime.now().isoformat(), ))
        await asyncio.sleep(1)
```