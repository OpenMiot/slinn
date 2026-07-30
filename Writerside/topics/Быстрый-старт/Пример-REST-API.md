# Пример REST API

В `app.py` приложения (или где прописан диспатчер):
```Python
from slinn import ApiDispatcher, AsyncRequest, HttpResponse
from slinn.utils import representate_str
import json


dp = ApiDispatcher()
users = []


@dp.get('/users')
async def list_users(request: AsyncRequest) -> HttpResponse:
    return HttpResponse(representate_str({ 'users': users }))


@dp.post('/users')
async def create_user(request: AsyncRequest) -> HttpResponse:
    data = await request.body.get()
    try:
        user = json.loads(data)
        users.append(
            { 'name': user['name'], 'age': int(user.get('age')) }
        )
    except (json.decoder.JSONDecodeError, KeyError, ValueError):
        return HttpResponse(
            { 'status': 'failed', 'message': 'invalid user data' },
            status='400 Bad Request'
        )
    return HttpResponse({'status': 'ok', 'id': len(users) - 1})


@dp.get('/users/<int user_id>')
async def get_user(
        request: AsyncRequest, user_id: int) -> HttpResponse:
    if user_id < 0 or user_id >= len(users):
        return HttpResponse(
            { 'status': 'notFound', 'message': 'user not found' },
            status='404 Not Found'
        )
    return HttpResponse(users[user_id])

```