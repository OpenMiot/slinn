# Dispatcher

Класс для обработки запросов

```Python
class slinn.Dispatcher (
    *hosts: str
)
```

1. `hosts` - хосты, на которых принимаются запросы

### Методы
- `__call__(_filter: Filter) -> Callable[[Callable], Callable]` - декоратор для создания хандлера
    1. `_filter` - фильтр хандлера
- `check(host: str) -> bool` - проверка на доступность диспатчера по указанному хосту
    1. `host` - хост для проверки
- `static(link: str, response_class: type[TCPResponseChunk], *args, **kwargs) -> Dispatcher` - создание асинхронного статического хандлера
    1. `link` - ссылка на хандлер
    2. `http_response` - класс ответа
    3. `args` и `kwargs` - аргументы конструктора класса ответа
- `sstatic(link: str, response_class: type[TCPResponseChunk], *args, **kwargs) -> Dispatcher` - создание статического хандлера
    1. `link` - ссылка на хандлер
    2. `http_response` - класс ответа
    3. `args` и `kwargs` - аргументы конструктора класса ответа

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
            <td><code>handles</code></td>
            <td>хандлеры, обрабатывающие запросы</td>
            <td><code>[]</code></td>
            <td><code>list[slinn.Handle]</code></td>
        </tr>
        <tr>
            <td><code>hosts</code></td>
            <td>хосты, на которых принимаются запросы</td>
            <td><code>('.*', )</code></td>
            <td><code>tuple[str]</code></td>
        </tr>
    </tbody>
</table>
