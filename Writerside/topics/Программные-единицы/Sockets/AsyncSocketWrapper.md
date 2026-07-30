# AsyncSocketWrapper

Класс-адаптер для асинхронного сокета

Наследуется от `slinn.SocketWrapper`

```Python
class slinn.AsyncSocketWrapper(
    sock: socket.socket,
    loop: asyncio.AbstractEventLoop,
    timeout: float = 5
)
```

1. `sock` - сокет;
2. `loop` асинхронный цикл событий;
3. `timeout` - таймаут подключения сокета в секундах.

### Методы

- `async do_handshake()` - выполнить ssl-рукопожатие;
- `async recv(n_bytes: int) -> bytes` - получает не более указанного количества байт:
    1. `n_bytes` - максимальное количество байт;
- `async send(data: bytes) -> int` - отправляет данные в сокет:
    1. `data` - данные;
- `async sendall(data: bytes) -> int` - отправляет данные в сокет:
    1. `data` - данные;
- `paste(data: bytes)` - возвращает данные в буфер:
    1. `data` - данные;
- `settimeout(timeout: float)` - устанавливает таймаут в секундах:
    1. `timeout` - таймаут;
- `setblocking(self, blocking: bool)` - устанавливает блокирующий или неблокирующий сокет:
    1. `blocking` - является ли сокет блокирующим;
- `getsockopt(self, *args) -> int | bytes` - получает настройки сокета;
- `fileno() -> int` - получает `fileno` сокета;
- `close()` - закрывает сокет;
- `closed() -> bool` - проверяет, является ли сокет закрытым.

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="15%">поле</th>
            <th width="40%">описание</th>
            <th width="14%">значение</th>
            <th width="31%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>_sock</code></td>
            <td>сокет</td>
            <td></td>
            <td><code>socket.socket</code></td>
        </tr>
        <tr>
            <td><code>loop</code></td>
            <td>асинхронный цикл событий</td>
            <td></td>
            <td><code>asyncio.AbstractEventLoop</code></td>
        </tr>
        <tr>
            <td><code>buffer</code></td>
            <td>буфер сокета</td>
            <td><code>bytearray()</code></td>
            <td><code>bytearray</code></td>
        </tr>
        <tr>
            <td><code>timeout</code></td>
            <td>таймаут подключения сокета в секундах</td>
            <td><code>5</code></td>
            <td><code>float</code></td>
        </tr>
    </tbody>
</table>