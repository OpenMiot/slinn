# EmptyHttpResponse

Объект класса является сборщиком пустого HTTP-ответа (статус `204 No Content`)

Наследуется от `slinn.HttpResponse`

```Python
class slinn.EmptyHttpResponse ()
```

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
            <td><code>''</code></td>
            <td><code>Any</code></td>
        </tr>
        <tr>
            <td><code>data</code></td>
            <td>HTTP-заголовки ответа</td>
            <td><code>[('Content-Length', 0), ('Content-Type', 'text/plain; charset=utf-8'), ('Server', slinn.version), ('Connection', 'Keep-Alive')]</code></td>
            <td><code>list[tuple] | None</code></td>
        </tr>
        <tr>
            <td><code>status</code></td>
            <td>HTTP-код ответа</td>
            <td><code>'204 No Content'</code></td>
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
