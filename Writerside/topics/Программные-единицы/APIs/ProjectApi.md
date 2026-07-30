# ProjectAPI

Класс реализует интерфейс для взаимодействия со Slinn проектом

### Методы

- `@staticmethod get_config() -> dict` - возвращает конфиг;
- `@staticmethod update_config(updates: Optional[dict] = None)` - обновляет конфиг;
- `@staticmethod create_app(name: str, hosts: tuple[str, ...] = (), *, init: bool = True)` - создает приложение:
    1. `name` - название-идентификатор приложения;
    2. `hosts` - хосты, с которыми будет работать это приложение;
    3. `init` - необходимо ли создавать базовую структуру (файлы `__init__.py`, `app.py`, `config.json`);
- `@staticmethod create_app_from_template(name: str, template_name: str, path: str = '.', templates_folder = slinn.root + '/templates')` - создать приложение по шаблону:
    1. `name` - название-идентификатор приложения;
    2. `template_name` - название-идентификатор шаблона;
    3. `path` - путь, в котором создается приложение;
    4. `templates_folder` - папка с шаблонами;
- `@staticmethod delete_app(name: str, path: str = '.')` - удалить приложение:
    1. `name` - название-идентификатор приложения;
    2. `path` - путь, в котором находится приложение;
- `@staticmethod set_project_name(name: str)` - установить название проекта:
    1. `name` - название проекта;
- `@staticmethod set_host(host: str)` - установить базовый хост проекта:
    1. `host` - базовый хост проекта;
- `@staticmethod set_port(port: int)` - установить порт, на котором запускается сервер проекта:
    1. `port` - порт;
- `@staticmethod disable_ssl()` - отключает ssl;
- `@staticmethod set_ssl_certs(public_cert_path: str, private_cert_path: str)` - устанавливает ssl-сертфикаты:
    1. `public_cert_path` - путь до публичного fullchain сертификата;
    2. `private_cert_path` - путь до private ключа;
- `@staticmethod set_debug(mode: bool)` - устанавливает _debug_-режим:
    1. `mode` - включить _debug_;
- `@staticmethod get_apps() -> set[str]` - получает множество названий приложений в проекте;
- `@staticmethod get_name() -> str` - получает название проекта;
- `@staticmethod is_ssl() -> bool` - проверяет, установлен ли ssl для сервера проекта;
- `@staticmethod get_link() -> str` - получает ссылку на сервер проекта;
- `@staticmethod restart()` - перезапускает процесс;
- `@staticmethod get_plugins() -> list[dict]` - получает список установленных плагинов;
- `@staticmethod get_plugin_storage(key: str) -> slinn.Storage` - получает хранилище плагина:
    1. `key` - идентификатор плагина.

