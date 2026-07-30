# HttpResponseChunk

Объект класса используется для отправки частей HTTP-ответов

Наследуется от `slinn.TCPResponseChunk`

```Python
class slinn.HttpResponseChunk (
    payload: typing.Any
)
```

1. `payload` - полезная нагрузка ответа

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
