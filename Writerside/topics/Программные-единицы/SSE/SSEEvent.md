# SSEEvent

Класс SSE события

Наследуется от `slinn.HttpResponseChunk`

```Python
class slinn.SSEEvent (
    *,
    event: Optional[str] = None,
    event_id: Optional[str] = None,
    full_data: Optional[Iterable[str]] = None,
    retry: Optional[int] = None,
    comments: Optional[str] = None
)
```

1. `event` - тип события
2. `event_id` - идентификатор события
3. `full_data` - данные события
4. `retry` - указывает, сколько миллисекунд ждать клиенту при переподключении
5. `comments` - комментарии к событию

### Методы
- `make(version: str = 'HTTP/1.1') -> bytes` - возвращает байтовое представление ответа (готовое к отправке по сокету)
    1. `version` - версия HTTP

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="24%">поле</th>
            <th width="34%">описание</th>
            <th width="32%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>payload</code></td>
            <td>полезая нагрузка ответа</td>
            <td><code>Any</code></td>
        </tr>
    </tbody>
</table>
