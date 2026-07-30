# TCPResponseChunk

Объект класса используется для отправки TCP-ответов 

```Python
class slinn.TCPResponseChunk (
    payload: typing.Any
)
```

1. `payload` - полезная нагрузка ответа

### Методы
- `make() -> bytes` - возвращает байтовое представление ответа (готовое к отправке по сокету)

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
