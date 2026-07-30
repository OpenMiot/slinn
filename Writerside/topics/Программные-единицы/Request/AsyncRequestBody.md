# AsyncRequestBody

Объект класса является асинхронным инструментом для чтения тела HTTP-запроса 

Наследуется от `slinn.RequestBody`

```Python
class slinn.AsyncRequestBody (
    request: slinn.AsyncRequest
)
```

1. `request` - `AsyncRequest` заголовок запроса

### Методы
- `size() -> int` - возвращает размер тела запроса исходя из `Content-Length`;
- `end() -> bool` - проверяет, был ли достигнут конец тела запроса;
- `until_end() -> int` - возвращает размер непрочитанного тела;
- `async recv(n_bytes: int) -> bytes` - читает часть тела запроса;
    1. `n_bytes` - максимальное количество байт, которое необходимо прочитать;
- `async receive() -> bytes` - читает тело запроса до лимита в `slinn.Server.max_bytes_per_receive`;
- `async getline() -> bytes` - читает одну строку (CRLF) из тела запроса;
- `async get() -> bytes` - читает тело запроса целиком;
- `async form() -> dict` - обрабатывает тело запроса как `application/x-www-form-urlencoded` форму;
- `async skip() -> None` - пропускает тело запроса;
- `files_boundary() -> typing.Optional[str]` - возвращает `boundary` из `multipart/form-data`;
- `async next_file_header() -> dict` - читает заголовок файла из `multipart/form-data`;
- `async next_file_body() -> bytes` - читает тело файла из `multipart/form-data`.
