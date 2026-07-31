# AsyncWebSocketGroup

Класс для объединения нескольких асинхронных Websocket подключений в одну группу

```Python
class AsyncWebSocketGroup ()
```

### Методы

- `__getattr__(key: str) -> Callable[..., Awaitable[list[WebSocketFrame]]]` - возвращаает один из методов для всех подключений группы
    1. `key` - название метода (`read`, `_send`, `send_binary`, `send_text`, `ping`, `pong`, `close`, `send`)
- `add(connection: AsyncWebSocketConnection)` - добавляет подключение в группу
    1. `connection` - подключение
- `add_subgroup(self, subgroup: AsyncWebSocketGroup)` - добавляет подгруппу в группу
    1. `subgroup` - подгруппа

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="19%">поле</th>
            <th width="35%">описание</th>
            <th width="17%">значение</th>
            <th width="29%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>connections</code></td>
            <td>список подключений</td>
            <td><code>[]</code></td>
            <td><code>list[slinn.AsyncWebSocketConnection]</code></td>
        </tr>
        <tr>
            <td><code>subgroups</code></td>
            <td>список подгрупп</td>
            <td><code>[]</code></td>
            <td><code>list[slinn.AsyncWebSocketGroup]</code></td>
        </tr>
    </tbody>
</table>
