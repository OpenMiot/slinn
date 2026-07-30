# FTDispatcher

Класс для обработки типов файлов

```Python
class slinn.FTDispatcher ()
```

### Методы

- `by_extension(extension: str) -> Callable[[Callable], Callable]` - декоратор для обработки типа файлов по расширению;
    1. `extension` - расширение файла;
- `by_regexp(regexp: str) -> Callable[[Callable], Callable]` - декоратор для обработки типа файлов по регулярному выражению;
    1. `regexp` - регулярное выражение.

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
            <td><code>handles</code></td>
            <td>список хандлеров для типов файлов</td>
            <td><code>[]</code></td>
            <td><code>list[slinn.Handle]</code></td>
        </tr>
    </tbody>
</table>
