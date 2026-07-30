# LinkFilter

Класс для фильтрации запросов по ссылке

Наследуется от `slinn.Filter`

```Python
class slinn.LinkFilter (
    _filter: str,
    methods: tuple[str, ...] = ('GET', 'POST')
)
```

1. `_filter` - регулялрное выражение для фильтрации (применяется к ссылке запроса `Request.link`)
2. `methods` - HTTP-методы, по которым срабатывает фильтр

### Методы

- `check(request: slinn.Request) -> bool` - проверить запрос на соблюдение условий фильтра
    1. `request` - проверяемый запрос
- `size(request: slinn.Request) -> int` - коэффициент запроса по фильтру для Smart Navigation
    1. `request` - запрос для получения коэффициента
- `args(*args, **kwargs) -> dict` - передача аргументов в фильтр
    1. `args` и `kwargs` - аргументы для передачи в фильтр

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="15%">поле</th>
            <th width="41%">описание</th>
            <th width="17%">значение</th>
            <th width="27%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>filter</code></td>
            <td>ссылка для фильтрации с регулярным выражением (применяется к ссылке запроса <code>Request.link</code>)</td>
            <td></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>methods</code></td>
            <td>HTTP-методы, по которым срабатывает фильтр</td>
            <td><code>('GET', 'POST')</code></td>
            <td><code>tuple[str]</code></td>
        </tr>
    </tbody>
</table>
