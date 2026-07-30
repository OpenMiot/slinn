# HttpJSONResponse

Объект класса является сборщиком HTTP-ответа формата `JSON` из множества аргументов

Наследуется от `slinn.HttpResponse`

```Python
class slinn.HttpJSONResponse (
    **payload: Any
)
```
1. `payload` - полезная нагрузка ответа. Также следующие аргументы обрабатываются отдельно и не собираются в `JSON`:
    - `__data` - HTTP-заголовки ответа;
    - `__status` - HTTP-код ответа;
    - `__content_type` - `Content-Type` заголовок.

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
            <td><code>dict</code>, может быть <code>Any</code></td>
        </tr>
        <tr>
            <td><code>data</code></td>
            <td>HTTP-заголовки ответа</td>
            <td><code>[('Content-Length', len(payload)), ('Content-Type', content_type), ('Server', slinn.version), ('Connection', 'Keep-Alive')]</code></td>
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
