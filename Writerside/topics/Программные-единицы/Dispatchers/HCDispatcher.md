# HCDispatcher

Класс для обработки HTTP-кодов

```Python
class slinn.HCDispatcher ()
```

### Методы

- `__getitem__(key: int) - Handle` - получить хандлер по HTTP-коду;
    1. `key` - HTTP-код;
- `__call__(code: int) -> Callable[[Callable], Callable]` - декоратор для создания хандлера по HTTP-коду;
    1. `code` - HTTP-код.

### Поля

<table width="100%">
    <thead>
        <tr>
            <th width="15%">поле</th>
            <th width="40%">описание</th>
            <th width="14%">значение</th>
            <th width="31%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>functions</code></td>
            <td>словарь с хандлерами по HTTP-кодам</td>
            <td><code>{}</code></td>
            <td><code>dict[int, slinn.Handle]</code></td>
        </tr>
    </tbody>
</table>
