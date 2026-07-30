# SSEHeader

Класс SSE заголовка

Наследуется от `slinn.HttpResponseHeader`

```Python
class slinn.SSEHeader (
    cors: Optional[str] = None
)
```

1. `cors` - заголовок `Access-Control-Allow-Origin`

### Методы

- `set_cookie(
        key: str,
        value: typing.Any,
        domain: typing.Optional[str] = None,
        expires: typing.Optional[datetime.datetime] = None,
        http_only: typing.Optional[bool] = None,
        max_age: typing.Optional[int] = None,
        partitioned: typing.Optional[bool] = None,
        path: typing.Optional[str] = None,
        secure: typing.Optional[bool] = None,
        same_site: typing.Optional[CookieSameSite] = None,
        attributes: typing.Optional[dict] = None
    ) -> slinn.HttpResponseChunk` - устанавливает HTTP-заголовок `Set-Cookie`:
  1. `key` - имя cookie;
  2. `value` - значение cookie;
  3. `domain` - хост, на который будут отправляться cookie;
  4. `expires` - максимальное время жизни cookie;
  5. `http_only` - запрещает JavaScript доступ к cookie;
  6. `max_age` - количество секунд, после которых cookie устаревает;
  7. `partitioned` - используется механизм CHIPS;
  8. `path` - путь, который должен существовать в запрошенном URL;
  9. `secure` - cookie будет отправлен только с использованием TLS/SSL;
  10. `same_site` - может быть:
      - `slinn.CookieSameSite.STRICT` - cookie отправляется только при внутрисайтовых запросах;
      - `slinn.CookieSameSite.LAX` - cookie не отправляется при межсайтовых запросах, но отправляется когда пользователь сам переходит на внешний сайт;
      - `slinn.CookieSameSite.NONE` - cookie отправляется как при внутрисайтовых запросах, так и при межсайтовых;

- `make` метод наследуется от `slinn.HttpResponseChunk`.

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
            <td>полезая нагрузка ответа (устанавливается после вызова метода <code>make</code>)</td>
            <td><code>''</code></td>
            <td><code>Any</code></td>
        </tr>
        <tr>
            <td><code>data</code></td>
            <td>HTTP-заголовки ответа</td>
            <td><code>[('Content-Type', content_type), ('Server', slinn.version), ('Connection', 'Keep-Alive')]</code></td>
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
