# HttpRender

Объект класса является движком для рендера файла и сборки HTTP-ответа

Наследуется от `slinn.HttpResponse`

```Python
class slinn.HttpRender (
    file_path: str,
    data: typing.Optional[list[tuple]] = None,
    status: str = '200 OK',
    ppdata: typing.Optional[dict] = None,
    storage = open,
    request: typing.Optional[Request] = None
)
```
1. `file_path` - путь до файла
2. `data` - HTTP-заголовки ответа
3. `status` - HTTP-код ответа
4. `ppdata` - словарь с переменными для препроцессора
5. `storage` - хранилище, через которое движок открывает файл
6. `request` - ссылка на запрос

### Методы

- `set_cookie` наследуется от `slinn.HttpResponse`
- `make(version: str = 'HTTP/1.1', htrf: typing.Optional[FTDispatcher] = None) -> bytes` - возвращает байтовое представление ответа (готовое к отправке по сокету)
    1. `version` - версия HTTP
    2. `htrf` - диспатчер для типов файлов

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
            <td><code>file_path</code></td>
            <td>путь до файла</td>
            <td></td>
            <td><code>str</code></td>
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
            <td><code>ppdata</code></td>
            <td>словарь с переменными для препроцессора</td>
            <td><code>None</code></td>
            <td><code>dict[str, Any] | None</code></td>
        </tr>
        <tr>
            <td><code>storage</code></td>
            <td>хранилище, через которое движок открывает файл</td>
            <td><code>open</code></td>
            <td><code>Storage</code></td>
        </tr>
    </tbody>
</table>
