# Handle

Структура обработчика запросов

```Python
class Handle (
    _filter: Filter,
    function: Callable,
    args: Callable[..., dict] = lambda *args, **kwargs: {}
)
```

1. `_filter` - фильтр обработчика;
2. `function` - функция обработчика;
3. `args` - метод извлечения аргументов из запроса.
