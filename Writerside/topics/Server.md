# Server

```Python
class slinn.Server(
    *dispatchers: Any,
    smart_navigation: bool = True,
    ssl_fullchain: typing.Optional[str] = None,
    ssl_key: typing.Optional[str] = None,
    timeout: float = 5,
    max_bytes_per_receive: int = 65535,
    max_header_size: int = 8192,
    _func: typing.Optional[typing.Callable] = None,
    logger: typing.Optional[logging.Logger] = None,
    hcdp: typing.Optional[slinn.HCDispatcher] = None,
    htrf: typing.Optional[slinn.FTDispatcher] = None,
    max_requests: int = 200,
    debug: bool = True
)
```
1. `dispatcher` - диспатчеры, которые нужно загрузить для работы сервера
2. `smart_navigation` - включить или выключить режим _Smart Navigation_
3. `ssl_fullchain` - путь до fullchain ssl сертификата
4. `ssl_key` - путь до закрытого ssl сертификата
5. `timeout` - таймаут подключений по умолчанию
6. `max_bytes_per_receive` - максимальное количество байт, которое примет подключение за один раз. Зависит от размера окна TCP
7. `max_header_size` - максимальное количество байт на заголовок запроса
8. `_func` - функция, которая вызывается перед каждым запросом. Принимает единственный аргумент - вызывающий сервер
9. `logger` - логгер
10. `hcdp` - диспатчер для HTTP-кодов
11. `htrf` - диспатчер для типов файлов
12. `max_requests` - максимальное количество запросов на подключение по умолчанию
13. `debug` - включен ли режим _debug_

### Методы
- `reload(*dispatchers: slinn.Dispatcher) -> None` - перезагружает диспатчеры.
  1. `dispatchers` - диспатчеры, которые нужно загрузить вместо текущих;
- `exit() -> None` - завершает работу сервера.
- `address(port: int, domain: str = None) -> None` - возвращает сообщение с ссылкой, по которой доступен HTTP-сервер.
  1. `port` - порт;
  2. `domain` - домен/хост.
- `listen(address: slinn.Address) -> None` - запускает сервер.
  1. `address` - адрес, по которому будет доступен сервер.
- `handle_request(connection: slinn.SocketWrapper, client_address: tuple, wrapped: bool = False, timeout: bool = None, max_requests: bool = None) -> None` - обрабатывает подключение от клиента.
  1. `connection` - подключение от клиента;
  2. `client_address` - пара в кортеже IP-порт;
  3. `wrapped` - не используется;
  4. `timeout` - переопределение таймаута по умолчанию;
  5. `max_requests` - переопределение максимального количества запросов на подключение по умолчанию.
- `answer_request(client_socket: slinn.SocketWrapper, handle: slinn.Handle, request: slinn.Request, http_data: bytearray, http_header: str, max_requests: int) -> bool:` - пытается ответить на запрос выбранным хандлером, возвращает `True` если получилось
  1. `client_socket` - подключение от клиента;
  2. `handle` - хандлер;
  3. `request` - запрос;
  4. `http_data` - сериализованный HTTP запроса (фактически только заголовок);
  5. `http_header` - заголовок запроса;
  6. `max_requests` - переопределение максимального количества запросов на подключение по умолчанию.
