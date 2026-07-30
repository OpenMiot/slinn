# AsyncWebSocketConnection

Класс-фасад асинхронного Websocket подключения

Наследуется от `slinn.WebSocketConnection`

```Python
class slinn.AsyncWebSocketConnection (
    request: slinn.AsyncRequest
)
```

1. `request` - запрос, инициирующий WebSocket подключение.

### Методы

- `async handshake()` - выполняет рукопожатие;
- `async _send(opcode: WebSocketOpcodes, payload: bytes)` - выполняет операцию;
    1. `opcode` - код операции;
    2. `payload` - полезная нагрузка операции;
- `async send_binary(payload: bytes)` - отправляет бинарные данные;
    1. `payload` - данные;
- `async send_text(payload: str)` - отправляет строку;
    1. `payload` - строка;
- `async ping()` - пингует клиент;
- `async pong()` - отвечает на пинг;
- `async close(reason: str = '')` - закрывает соединение;
    1. `reason` - причина закрытия;
- `settimeout(timeout: float)` - устанавливает таймаут между фреймами:
  - `timeout` - таймаут;
- `async send(payload: bytes | str)` - отправляет бинарные или строковые данные;
    1. `payload` - данные;
- `async read() -> slinn.WebSocketFrame` - возвращает полученный WebSocket фрейм.

### Свойства

<table width="100%">
    <thead>
        <tr>
            <th width="20%">свойство</th>
            <th width="45%">описание</th>
            <th width="35%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>closed</code></td>
            <td>является ли сокет закрытым</td>
            <td><code>bool</code></td>
        </tr>
    </tbody>
</table>

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="19%">поле</th>
            <th width="46%">описание</th>
            <th width="35%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>request</code></td>
            <td>запрос, инициирующий WebSocket подключение</td>
            <td><code>slinn.AsyncRequest</code></td>
        </tr>
    </tbody>
</table>

### Примечания

`read()` автоматически закрывает соединение (отправляет закрывающий опкод и закрывает TCP) при получении опкода на
закрытие
