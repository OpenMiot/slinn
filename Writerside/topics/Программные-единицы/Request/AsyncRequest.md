# AsyncRequest

Объект класса является представлением заголовка HTTP-запроса для асинхронного сервера

Наследуется от `slinn.Request`

```Python
class slinn.AsyncRequest (
    loop: asyncio.AbstractEventLoop,
    header: str,
    client_address: tuple[str, int],
    connection: slinn.AsyncSocketWrapper,
    server: slinn.AsyncServer,
    htrf: Optional[slinn.FTDispatcher] = None
)
```

1. `loop` - асинхронный цикл событий;
2. `header` - сериализованный HTTP-заголовок запроса;
3. `client_address` - пара в кортеже IP-порт;
4. `connection` - подключение от клиента;
5. `server` - ссылка на сервер, который принял запрос;
6. `htrf` - переопределенный диспатчер для типов файлов.

### Методы
- `__repr__() -> str` - возвращает текстовое представление запроса;
- `__str__() -> str` - возвращает текстовое представление запроса;
- `async respond(response_class: type[TCPResponseChunk], *args, **kwargs) -> None` - отвечает на запрос;
    1. `response_class` - класс ответа;
    2. `args` и `kwargs` - аргументы конструктора экземляра класса ответа;
- `async recv(n_bytes: int) -> bytes` - возвращает не более указанного количества байт, пришедших в соединение;
    1. `n_bytes` - максимальное количество байт;
- `async WebSocket(timeout: float) -> slinn.AsyncWebSocketConnection` - создает и возвращает WebSocket соединение:
  - `timeout` - таймаут для соединения.

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="17%">поле</th>
            <th width="50%">описание</th>
            <th width="23%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>type</code></td>
            <td>первая строка HTTP-запроса (Request Line)</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>header</code></td>
            <td>
                словарь, включающий в себя:
                <ul>
                    <li><code>method</code> - HTTP-метод;</li>
                    <li><code>link</code> - ссылку (вместе с GET-аргументами);</li>
                    <li><code>ver</code> - полную версию HTTP (например, <code>HTTP/1.1</code>);</li>
                    <li><code>data</code> - словарь с заголовками запроса</li>
                </ul>
            </td>
            <td><code>dict[str, str]</code></td>
        </tr>
        <tr>
            <td><code>payload</code></td>
            <td>полезная нагрузка, всегда равна <code>b''</code> (устарело, необходимо для совместимости с <i>Murega</i>)</td>
            <td><code>bytes</code></td>
        </tr>
        <tr>
            <td><code>files</code></td>
            <td>список переданных файлов, всегда пустой (устарело, необходимо для совместимости с <i>Murega</i>)</td>
            <td><code>list</code>, <code>.__len__() == 0</code></td>
        </tr>
        <tr>
            <td><code>ip</code></td>
            <td>IP-адрес клиента</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>port</code></td>
            <td>порт клиента</td>
            <td><code>int</code></td>
        </tr>
        <tr>
            <td><code>protocol</code></td>
            <td>протокол. Обычно равен <code>HTTP</code>, за исключением искусственно созданных случаев</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>version</code></td>
            <td>числовая версия HTTP (например, <code>1.1</code>)</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>full_link</code></td>
            <td>ссылка (вместе с GET-аргументами)</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>headers</code></td>
            <td>словарь с заголовками запроса</td>
            <td><code>dict[str, str]</code></td>
        </tr>
        <tr>
            <td><code>host</code></td>
            <td>домен, на который пришел запрос (заголовок <code>Host</code>)</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>user_agent</code></td>
            <td>агент клиента (заголовок <code>User-Agent</code>)</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>accept</code></td>
            <td>заголовок <code>Accept</code></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>encoding</code></td>
            <td>заголовок <code>Accept-Encoding</code></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>language</code></td>
            <td>заголовок <code>Accept-Language</code></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>link</code></td>
            <td>ссылка без GET-аргументов</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>args</code></td>
            <td>словарь с GET-аргументами</td>
            <td><code>dict[str, str]</code></td>
        </tr>
        <tr>
            <td><code>cookies</code></td>
            <td>словарь с Cookie</td>
            <td><code>dict[str, str]</code></td>
        </tr>
        <tr>
            <td><code>content_length</code></td>
            <td>длина полезной нагрузки (заголовок <code>Content-Length</code>)</td>
            <td><code>int</code></td>
        </tr>
        <tr>
            <td><code>content_type</code></td>
            <td>тип MIME полезной нагрузки (заголовок <code>Content-Type</code>)</td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>keep_alive</code></td>
            <td>заголовок <code>Keep-Alive</code></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>connection</code></td>
            <td>подключение от клиента</td>
            <td><code>SocketWrapper</code></td>
        </tr>
        <tr>
            <td><code>server</code></td>
            <td>ссылка на сервер, который принял запрос</td>
            <td><code>Server</code></td>
        </tr>
        <tr>
            <td><code>htrf</code></td>
            <td>переопределенный диспатчер для типов файлов</td>
            <td><code>FTDispatcher</code></td>
        </tr>
        <tr>
            <td><code>body</code></td>
            <td>тело запроса</td>
            <td><code>AsyncRequestBody</code></td>
        </tr>
        <tr>
            <td><code>loop</code></td>
            <td>асинхронный цикл событий</td>
            <td><code>asyncio.AbstractEventLoop</code></td>
        </tr>
    </tbody>
</table>
