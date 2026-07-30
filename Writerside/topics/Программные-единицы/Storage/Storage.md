# Storage

Класс для создания файловых хранилищ (в виде каталогов или `.zip` архивов)

```Python
class Storage (
    root: str = '',
    package: Optional[str] = None,
    *,
    zip_file: bool | str = False
)
```

1. `root` - путь до корневого каталога хранилища
2. `package` - пакет хранилища
3. `zip_file` - путь до `.zip` архива хранилища

### Методы

- `__call__(path: str, mode: str, encoding: str = 'utf-8') -> slinn.StorageIO` - открывает файл
    1. `path` - путь до файла
    2. `mode` - режим открытия файла
    3. `encoding` - кодировка файла
- `isfile(path: str) -> bool` - проверят, является ли объект файловой системы по пути файлом
    1. `path` - путь до объекта файловой системы
- `isdir(path: str) -> bool` - проверят, является ли объект файловой системы по пути каталогом
    1. `path` - путь до объекта файловой системы
- `listdir(path: str) -> list[str]` - возвращает список объектов файловой системы внутри каталога
    1. `path` - путь до каталога
- `mkdir(path: str, mode: int = 0o700)` - создает каталог
    1. `path` - путь до будущего каталога
    2. `mode` - права доступа к будущему каталогу
- `makedirs(path: str, mode: int = 0o700)` - создает каталоги
    1. `path` - путь до будущих каталогов
    2. `mode` - права доступа к будущим каталогов
- `remove(path: str)` - удаляет объект файловой системы
    1. `path` - путь до объекта файловой системы
- `rmtree(path: str)` - удаляет каталог со всем содержимым
    1. `path` - путь до каталога
- `substorage(path: str) -> slinn.Storage` - возвращает подхранилище из каталога
    1. `path` - путь до каталога подхранилища

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
            <td><code>root</code></td>
            <td>путь до корневого каталога хранилища</td>
            <td></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>package</code></td>
            <td>пакет хранилища</td>
            <td><code>None</code></td>
            <td><code>Optional[str]</code></td>
        </tr>
    </tbody>
</table>
