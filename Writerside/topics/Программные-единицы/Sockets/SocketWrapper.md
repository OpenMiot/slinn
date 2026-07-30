# SocketWrapper

Класс-адаптер для сокета

```Python
class slinn.SocketWrapper(
    sock: socket.socket,
    timeout: float = 5
)
```

1. `sock` - сокет;
2. `timeout` - таймаут подключения сокета в секундах.

### Методы

- `recv(n_bytes: int) -> bytes` - получает не более указанного количества байт:
    1. `n_bytes` - максимальное количество байт;
- `send(data: bytes) -> int` - отправляет данные в сокет:
    1. `data` - данные;
- `sendall(data: bytes) -> int` - отправляет данные в сокет:
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