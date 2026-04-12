# Request

```Python
class Request(
    header: str,
    client_address: tuple[str, int],
    connection: slinn.SocketWrapper,
    server: slinn.Server,
    htrf: typing.Optional[slinn.FTDispatcher] = None
)
```

1. `header` - сериализованный HTTP-заголовок запроса;
2. `client_address` - пара в кортеже IP-порт;
3. `connection` - подключение от клиента;
4. `server` - ссылка на сервер, который принял запрос;
5. `htrf` - переопределенный диспатчер для типов файлов.

### Методы
- `__repr__() -> str` - возвращает текстовое представление запроса;
- `__str__() -> str` - возвращает текстовое представление запроса;
- `respond(response_class: TCPResponseChunk, *args, **kwargs) -> None` - отвечает на запрос;
    1. `response_class` - класс ответа;
    2. `args` и `kwargs` - аргументы конструктора экземляра класса ответа;
- `recv(n_bytes: int) -> bytes` - возвращает не более указанного количества байт, пришедших в соединение;
- `WebSocket() -> WebSocketConnection` - создает и возвращает WebSocket соединение.

### Поля
- `type` - первая строка HTTP-запроса (Request Line);
- `header` - словарь, включающий в себя:
  - `method` - HTTP-метод;
  - `link` - ссылку (вместе с GET-аргументами);
  - `ver` - полную версию HTTP (например, `HTTP/1.1`);
  - `data` - словарь с заголовками запроса.
- `payload` - полезная нагрузка, всегда равна `b''` (устарело, необходимо для совместимости с _Murega_);
- `files` - список переданных файлов, всегда пустой (устарело, необходимо для совместимости с _Murega_);
- `ip` - IP-адрес клиента
- `port` - порт клиента
- `protocol` - протокол. Обычно равен `HTTP`, за исключением искусственно созданных случаев
- `version` - числовая версия HTTP (например, `1.1`)
- `full_link` - ссылка (вместе с GET-аргументами)
- `headers` - словарь с заголовками запроса
- `host` - домен, на который пришел запрос (заголовок `Host`)
- `user_agent` - агент клиента (заголовок `User-Agent`)
- `accept` - заголовок `Accept`
- `encoding` - заголовок `Accept-Encoding`
- `language` - заголовок `Accept-Language`
- `link` - ссылка без GET-аргументов
- `args` - словарь с GET-аргументами
- `cookies` - словарь с Cookie
- `content_length` - длина полезной нагрузки (заголовок `Content-Length`)
- `content_type` - тип MIME полезной нагрузки (заголовок `Content-Type`)
- `keep_alive` - заголовок `Keep-Alive`
- `connection` - подключение от клиента
- `server` - ссылка на сервер, который принял запрос;
- `htrf` - переопределенный диспатчер для типов файлов
- `body` - `RequestBody` тело запроса
