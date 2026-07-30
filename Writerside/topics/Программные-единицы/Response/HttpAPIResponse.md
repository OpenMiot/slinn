# HttpAPIResponse

Объект класса является сборщиком HTTP-ответа из объектного представления с добавлением HTTP-заголовка `Access-Control-Allow-Origin: *`

Наследуется от `slinn.HttpResponse`

```Python
class slinn.HttpAPIResponse (
    payload: typing.Any,
    data: typing.Optional[list[tuple]] = None,
    status: str = '200 OK',
    content_type: str = 'text/plain; charset=utf-8',
    use_gzip: bool = True,
    request: typing.Optional[slinn.Request] = None
)
```
1. `payload` - полезная нагрузка ответа
2. `data` - HTTP-заголовки ответа
3. `status` - HTTP-код ответа
4. `content_type` - `Content-Type` заголовок
5. `use_gzip` - использовать сжатие gzip
6. `request` - ссылка на запрос

### Методы

- `set_cookie` наследуется от `slinn.HttpResponse`
- `make` наследуется от `slinn.HttpResponse`

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="15%">поле</th>
            <th width="35%">описание</th>
            <th width="27%">значение</th>
            <th width="23%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>payload</code></td>
            <td>полезая нагрузка ответа</td>
            <td></td>
            <td><code>Any</code></td>
        </tr>
        <tr>
            <td><code>data</code></td>
            <td>HTTP-заголовки ответа</td>
            <td><code>[('Content-Length', len(payload)), ('Content-Type', content_type), ('Server', slinn.version), ('Connection', 'Keep-Alive'), ('Access-Control-Allow-Origin', '*')]</code></td>
            <td><code>list[tuple] | None</code></td>
        </tr>
        <tr>
            <td><code>status</code></td>
            <td>HTTP-код ответа</td>
            <td><code>'200 OK'</code></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>use_gzip</code></td>
            <td>использовать сжатие gzip</td>
            <td><code>True</code></td>
            <td><code>bool</code></td>
        </tr>
    </tbody>
</table>
