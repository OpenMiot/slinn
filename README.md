
<div align="center">
    <h1>Slinn</h1>
    <b>Slinn - фреймворк для создания Web-приложений на языке Python</b><br/>
    <img src="https://img.shields.io/github/license/OpenMiot/slinn" alt="License"/>
    <img src="https://img.shields.io/github/languages/top/OpenMiot/slinn" alt="GitHub top language"/>
    <img src="https://img.shields.io/github/v/release/OpenMiot/slinn" alt="GitHub Release"/>
    <img src="https://img.shields.io/github/stars/OpenMiot/slinn" alt="GitHub Repo stars"/>
</div>

### Преимущества Slinn

- Асинхронность + параллелизм(опционально, в 3.15t)
- Поддержка плагинов и пакетный менеджер
- Гибкая декларативная настройка
- Поддержка любых сетевых протоколов
- Работа на нескольких портах в одном запущенном экземпляре

### Простой пример синтаксиса
```python
from slinn.net.http import HttpRouter, HttpRequest
from slinn.net.http.responses import HttpRedirect
from slinn.net.http.filters import AnyFilter


router = HttpRouter()


@router.get('api/<str method>')
async def api(request: HttpRequest, method: str):
    return {
        'status': 'ok',
        'method': method,
        'ip': request.ip
    }

@router.get()
@router.get('index')
async def index():
    return HttpRedirect('/helloworld')


@router(AnyFilter)
async def helloworld():
     return 'Hello world!'

```

### Начало проекта
#### Standart
```bash
slinn-admin create-project www
cd www
venv/bin/activate
slinn create-app localhost host=localhost host=127.0.0.1
```

Вставьте пример в `localhost/app.py`, затем запустите скрипт `start.bat` или `start.sh`

Для настройки проекта нужно редактировать конфиг `slinn.toml`

Для настройки приложения нужно редактировать `%app%/config.toml`


### Зависимости
- Python 3.15 и выше (желательно без GIL)
- `tomlkit` - управление конфигами
- `orjson` - более быстрая работы с json
- `babel` - локализация фреймворка
- `pydantic` - валидация конфигов
#### Опциональные зависимости
##### Средства разработки фреймворка (`dev`):
- `pytest` - тестирование фреймворка
- `pytest-asyncio` - тестирование асинхнронных функций
- `pytest-describe` - группировка тестов
- `pytest-mock` - более удобное создание моков
- `pytest-cov` - подсчет покрытия тестами
- `taskipy` - упрощение ввода команд
- `poetry` - сборка и публикация пакета на PyPI
##### Асинхронные событийные циклы, которые могут улучшить производительность (`alt_loop`):
- `winloop` - альтернативный асинхронный событийный цикл на Windows
- `uvloop` - альтернативный асинхронный событийный цикл на Linux/MacOS