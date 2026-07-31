# AsyncServer

Объект класса принимает асинхронные подключения, управляет диспатчерами, пишет логи

Наследуется от `slinn.Server`

```Python
class slinn.AsyncServer (
    *dispatchers: slinn.Dispatcher,
    smart_navigation: bool = True,
    ssl_fullchain: Optional[str] = None,
    ssl_key: Optional[str] = None,
    timeout: float = 5,
    max_timeout: float = 60,
    max_bytes_per_receive: int = 65535,
    max_header_size: int = 8192,
    _func: Optional[Callable] = None,
    logger: Optional[logging.Logger] = None,
    hcdp: Optional[HCDispatcher] = None,
    htrf: Optional[FTDispatcher] = None,
    max_requests: int = 200,
    debug: bool = True
)
```
1. `dispatcher` - диспатчеры, которые нужно загрузить для работы сервера;
2. `smart_navigation` - включить или выключить режим _Smart Navigation_;
3. `ssl_fullchain` - путь до fullchain ssl сертификата;
4. `ssl_key` - путь до закрытого ssl сертификата;
5. `timeout` - таймаут подключений по умолчанию;
6. `max_timeout` - максимальный таймаут подключений;
7. `max_bytes_per_receive` - максимальное количество байт, которое примет подключение за один раз. Зависит от размера окна TCP;
8. `max_header_size` - максимальное количество байт на заголовок запроса;
9. `_func` - функция, которая вызывается перед каждым запросом. Принимает единственный аргумент - вызывающий сервер;
10. `logger` - логгер;
11. `hcdp` - диспатчер для HTTP-кодов;
12. `htrf` - диспатчер для типов файлов;
13. `max_requests` - максимальное количество запросов на подключение по умолчанию;
14. `debug` - включен ли режим _debug_.

### Методы

- `reload(*dispatchers: slinn.Dispatcher) -> None` - перезагружает диспатчеры.
  1. `dispatchers` - диспатчеры, которые нужно загрузить вместо текущих;
- `exit() -> None` - завершает работу сервера.
- `address(port: int, domain: str = None) -> None` - возвращает сообщение с ссылкой, по которой доступен HTTP-сервер.
  1. `port` - порт;
  2. `domain` - домен/хост.
- `listen(address: slinn.Address) -> None` - запускает сервер.
  1. `address` - адрес, по которому будет доступен сервер.
- `handle_request(connection: slinn.AsyncSocketWrapper, client_address: tuple[str, int], wrapped: bool = False, timeout: Optional[float] = None, max_requests: Optional[int] = None) -> None` - обрабатывает подключение от клиента.
  1. `connection` - подключение от клиента;
  2. `client_address` - пара в кортеже IP-порт;
  3. `wrapped` - не используется;
  4. `timeout` - переопределение таймаута по умолчанию;
  5. `max_requests` - переопределение максимального количества запросов на подключение по умолчанию.
- `answer_request(client_socket: slinn.AsyncSocketWrapper, handle: slinn.Handle, request: slinn.Request, http_data: bytearray, http_header: str, max_requests: int) -> bool:` - пытается ответить на запрос выбранным хандлером, возвращает `True` если получилось
  1. `client_socket` - подключение от клиента;
  2. `handle` - хандлер;
  3. `request` - запрос;
  4. `http_data` - сериализованный HTTP запроса (фактически только заголовок);
  5. `http_header` - заголовок запроса;
  6. `max_requests` - переопределение максимального количества запросов на подключение по умолчанию.

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="17%">поле</th>
            <th width="43%">описание</th>
            <th width="11%">значение</th>
            <th width="29%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>dispatchers</code></td>
            <td>диспатчеры, которые нужно загрузить вместо текущих</td>
            <td></td>
            <td><code>tuple[slinn.Dispatcher]</code></td>
        </tr>
        <tr>
            <td><code>smart_navigation</code></td>
            <td>включить или выключить режим <i>Smart Navigation</i></td>
            <td><code>True</code></td>
            <td><code>bool</code></td>
        </tr>
        <tr>
            <td><code>server_socket</code></td>
            <td>сокет сервера</td>
            <td><code>None</code></td>
            <td><code>Optional[slinn.SocketWrapper]</code></td>
        </tr>
        <tr>
            <td><code>ssl</code></td>
            <td>включен ли ssl</td>
            <td></td>
            <td><code>bool</code></td>
        </tr>
        <tr>
            <td><code>ssl_cert</code></td>
            <td>путь до fullchain ssl сертификата</td>
            <td></td>
            <td><code>Optional[str]</code></td>
        </tr>
        <tr>
            <td><code>ssl_key</code></td>
            <td>путь до private ssl ключа</td>
            <td></td>
            <td><code>Optional[str]</code></td>
        </tr>
        <tr>
            <td><code>ssl_context</code></td>
            <td>ssl контекст</td>
            <td></td>
            <td><code>Optional[ssl.SSLContext]</code></td>
        </tr>
        <tr>
            <td><code>threads</code></td>
            <td><i>не используется</i></td>
            <td><code>[]</code></td>
            <td><code>list</code></td>
        </tr>
        <tr>
            <td><code>timeout</code></td>
            <td>таймаут подключений по умолчанию</td>
            <td><code>5</code></td>
            <td><code>float</code></td>
        </tr>
        <tr>
            <td><code>max_timeout</code></td>
            <td>максимальный таймаут подключений</td>
            <td><code>60</code></td>
            <td><code>float</code></td>
        </tr>
        <tr>
            <td><code>max_requests</code></td>
            <td>максимальное количество запросов на подключение по умолчанию</td>
            <td><code>200</code></td>
            <td><code>int</code></td>
        </tr>
        <tr>
            <td><code>max_bytes_per_receive</code></td>
            <td>максимальное количество байт, которое примет подключение за один раз. Зависит от размера окна TCP</td>
            <td><code>65535</code></td>
            <td><code>int</code></td>
        </tr>
        <tr>
            <td><code>max_header_size</code></td>
            <td>максимальное количество байт на заголовок запроса</td>
            <td><code>8192</code></td>
            <td><code>int</code></td>
        </tr>
        <tr>
            <td><code>func</code></td>
            <td>функция, которая вызывается перед каждым запросом. Принимает единственный аргумент - вызывающий сервер</td>
            <td></td>
            <td><code>Callable[[slinn.Server], None]</code></td>
        </tr>
        <tr>
            <td><code>logger</code></td>
            <td>логгер</td>
            <td></td>
            <td><code>logging.Logger</code></td>
        </tr>
        <tr>
            <td><code>hcdp</code></td>
            <td>диспатчер для HTTP-кодов</td>
            <td></td>
            <td><code>slinn.HCDispatcher</code></td>
        </tr>
        <tr>
            <td><code>htrf</code></td>
            <td>диспатчер для типов файлов</td>
            <td></td>
            <td><code>slinn.FTDispatcher</code></td>
        </tr>
        <tr>
            <td><code>debug</code></td>
            <td>включен ли режим <i>debug</i></td>
            <td><code>True</code></td>
            <td><code>bool</code></td>
        </tr>
        <tr>
            <td><code>loop</code></td>
            <td>асинхронный цикл событий</td>
            <td><code>None</code></td>
            <td><code>Optional[asyncio.AbstractEventLoop]</code></td>
        </tr>
    </tbody>
</table>