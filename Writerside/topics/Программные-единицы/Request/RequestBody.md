# RequestBody

Объект класса является инструментом для чтения тела HTTP-запроса

```Python
class slinn.RequestBody (
    request: slinn.Request
)
```

1. `request` - `Request` заголовок запроса

### Методы
- `size() -> int` - возвращает размер тела запроса исходя из `Content-Length`;
- `end() -> bool` - проверяет, был ли достигнут конец тела запроса;
- `until_end() -> int` - возвращает размер непрочитанного тела;
- `recv(n_bytes: int) -> bytes` - читает часть тела запроса;
    1. `n_bytes` - максимальное количество байт, которое необходимо прочитать;
- `receive() -> bytes` - читает тело запроса до лимита в `slinn.Server.max_bytes_per_receive`;
- `getline() -> bytes` - читает одну строку (CRLF) из тела запроса;
- `get() -> bytes` - читает тело запроса целиком;
- `form() -> dict` - обрабатывает тело запроса как `application/x-www-form-urlencoded` форму;
- `skip() -> None` - пропускает тело запроса;
- `files_boundary() -> typing.Optional[str]` - возвращает `boundary` из `multipart/form-data`;
- `next_file_header() -> dict` - читает заголовок файла из `multipart/form-data`;
- `next_file_body() -> bytes` - читает тело файла из `multipart/form-data`.
