
<div align="center">
    <h1>Slinn</h1>
    <b>Slinn - универсальная сетевая платформа на Python</b><br/>
    <img src="https://github.com/openmiot/slinn/actions/workflows/tests.yml/badge.svg?event=push&branch=flux" alt="Tests"/>
    <img src="https://img.shields.io/pypi/pyversions/slinn.svg?color=%2334D058" alt="Supported Python versions">
    <img src="https://img.shields.io/github/v/release/OpenMiot/slinn" alt="GitHub Release"/>
    <img src="https://img.shields.io/github/stars/OpenMiot/slinn" alt="GitHub Repo stars"/>
</div>

---

Документация: https://openmiot.github.io/slinn/

Исходный код: https://github.com/OpenMiot/slinn/

---
### Преимущества Slinn

- Асинхронность + параллелизм(только во Free-Threaded Python)
- Поддержка плагинов и пакетный менеджер
- Гибкая декларативная настройка
- Поддержка любых сетевых протоколов
- Работа на нескольких портах в одном запущенном экземпляре

### Простой пример синтаксиса
```python
from slinn.net.http import HttpRouter
from slinn.net.http.responses import HttpRedirect
from slinn.net.http.filters import AnyFilter
from slinn.net.address import Address


router = HttpRouter()


@router.get('api/<str method>')
async def api(client_address: Address, method: str):
    return {
        'status': 'ok',
        'method': method,
        'ip': client_address.host
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
- `uv` - управление зависимостями
#### Опциональные зависимости
##### Средства разработки фреймворка (`dev`):
- `pytest` - тестирование фреймворка
- `pytest-asyncio` - тестирование асинхнронных функций
- `pytest-describe` - группировка тестов
- `pytest-mock` - более удобное создание моков
- `pytest-cov` - подсчет покрытия тестами
- `taskipy` - упрощение ввода команд
- `zensical` - документация
##### Асинхронные событийные циклы, которые могут улучшить производительность (`alt_loop`):
- `winloop` - альтернативный асинхронный событийный цикл на Windows
- `uvloop` - альтернативный асинхронный событийный цикл на Linux/MacOS