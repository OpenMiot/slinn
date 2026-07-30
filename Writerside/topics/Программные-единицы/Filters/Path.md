# Path

Класс для фильтрации запросов по ссылке с извлечением аргументов

Наследуется от `slinn.IPath`

```Python
class slinn.Path (
    pattern: str,
    methods: tuple[str, ...] = ('GET', 'POST')
)
```

1. `pattern` - паттерн для фильтрации (применяется к ссылке запроса `Request.link`)
2. `methods` - HTTP-методы, по которым срабатывает фильтр

### Методы

- `check(request: slinn.Request) -> bool` - проверить запрос на соблюдение условий фильтра
    1. `request` - проверяемый запрос
- `size(request: slinn.Request) -> int` - коэффициент запроса по фильтру для Smart Navigation
    1. `request` - запрос для получения коэффициента
- `args(request: slinn.Request) -> dict` - передача аргументов в фильтр
    1. `request` - запрос из которого извлекаются аргументы

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
            <td><code>types</code></td>
            <td>словарь с типами аргументов</td>
            <td><code>{}</code></td>
            <td><code>dict[str, type]</code></td>
        </tr>
        <tr>
            <td><code>_pattern</code></td>
            <td>паттерн для фильтрации (применяется к ссылке запроса <code>Request.link</code>)</td>
            <td></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>filter</code></td>
            <td>регулялрное выражение для фильтрации (применяется к ссылке запроса <code>Request.link</code>)</td>
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

### Примечания

`pattern` имеет синтаксис типа `<ТИП_АРГУМЕНТА(str/int/float/...) НАЗВАНИЕ_АРГУМЕНТА>` (например, `\/users\/<int id>`).
Посреди паттерна ссылки вставляется аргумент в угловых кавычках с указанием типа (`int`, `float`, `str`) и названия
аргумента через пробел.

В отличие от `slinn.IPath`, `slinn.Path` делает необязательным указание первого слеша в паттерне ссылке и
экранирование слешей в ссылке


