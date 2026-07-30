# IMiddleware

Интерфейс для создания мидлварей

### Методы

- `@abstractmethod __init__(self, *args, **kwargs): ...` - конструктор мидлвари;
- `@abstractmethod __call__(self, func: Callable) -> Callable` - метод, вызывающийся при каждом запросе:
    1. `func` - функция обработчика запроса.

### Пример

```Python
from __future__ import annotations
from typing import Optional
from slinn import IMiddleware, HttpResponse
from slinn.utils import optional
import functools


async def get_user(
    request: 'AsyncRequest',
    db_pool: 'PoolProtocol'
) -> Optional[dict]:
    """
        Функция для получения пользователя из базы данных по
        HTTP-запросу
    """

...

class AuthMiddleware(IMiddleware):
    def __init__(self, db_pool: 'PoolProtocol'):
        super().__init__()
        self.db_pool = db_pool

    def __call__(self, func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user = await get_user(kwargs['request'], self.db_pool)
            
            if not user:  # Пользователя нет в базе данных
                return 401
            
            # Вызывается обработчик с дополнительным опциональным
            # аргументом `user`
            return await optional(  
                func,
                *args, **( kwargs | { 'user': user } )
            )

        return wrapper

...

dp: 'ApiDispatcher'
db_pool: 'PoolProtocol'

...

@dp.get('/getId')
@AuthMiddleware(db_pool)
async def get_profile(request: 'AsyncRequest', user: dict):
    return HttpResponse(user['id'])
```

В этом примере создается мидлварь для аутентификации. С помощью функции `get_user`, мидлварь получает профиль
пользователя. Если пользователя нет в базе данных, то мидлварь вместо запуска обработчика запроса, возвращает HTTP-код
`401 Unauthorized` как ответ на запрос, т.е обработчик не вызывается. Если пользователь есть в базе данных, то мидлварь
вызывает обработчик с указанием аргумента `user` через метод `slinn.utils.optional`.


### Примечания

Мидлвари могут складываться в цепочку:

```Python
class AdminOnly(IMiddleware):
    def __init__(self):
        super().__init__()

    def __call__(self, func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if 'user' not in kwargs:  # Не передан `user` аргумент
                return 401
            
            if kwargs['user'].role != 'admin':  # Не админ
                return 403
            
            return await optional(func, *args, **kwargs)

        return wrapper

...

@dp.get('/adminpanel')
@AuthMiddleware(db_pool)
@AdminOnly()
async def get_adminpanel(request: 'AsyncRequest', user: dict):
    ...


@dp.post('/halt')
@AuthMiddleware(db_pool)
@AdminOnly()
async def post_halt(request: 'AsyncRequest'):  # Нет аргумента `user`
    ...
```

В данном примере обработчик `get_adminpanel` вызовется только при условии, что `user` найден в базе данных и является
администратором. Однако, обработчик `post_halt` никогда не выполнится, а на запросы будет ответ всегда
`401 Unauthorized`. Такое поведение вызвано отсутствующим аргументом `user` в сигнатуре функции
обработчика `post_halt`. `slinn.utils.optional` не передаст аргумент `user` из `AuthMiddleware` в `AdminOnly`, поэтому
необходимо прописывать все используемые аргументы в мидлварях, даже если они не будут использоваться непосредственно в
обработчике.