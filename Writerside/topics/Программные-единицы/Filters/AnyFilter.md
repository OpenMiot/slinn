# AnyFilter

Объект класса `Filter`, принимающий любые запросы

```Python
AnyFilter = Filter(
    '.*',
    (
        'GET',
        'HEAD',
        'POST',
        'PUT',
        'DELETE',
        'CONNECT',
        'OPTIONS', 
        'TRACE',
        'PATCH'
    )
)
```