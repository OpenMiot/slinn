# StorageIO



```Python
class StorageIO (
    path: str,
    mode: str,
    encoding: str = 'utf-8',
    package: Optional[str] = None,
    _package_type: Optional[slinn.storage.PackageType] = None,
    _package_zip: Optional[str] = None
)
```

1. `path` - путь до файла
2. `mode` - режим чтения файла
3. `encoding` - кодировка файла
4. `package` - пакет файла
5. `_package_type` - тип пакета файла
6. `_package_zip` - архив, в котором находится файл

### Методы

- `__enter__() -> IO` - возвращает файловый поток
- `__exit__(_type, value, traceback)` - закрывает файловый поток
- `__getattr__(__name: str)` - возвращает атрибут файлового потока
    1. `__name` - название атрибута

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
            <td><code>path</code></td>
            <td>путь до файла</td>
            <td></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>mode</code></td>
            <td>режим чтения файла</td>
            <td></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>encoding</code></td>
            <td>кодировка файла</td>
            <td><code>'utf-8'</code></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>package</code></td>
            <td>пакет файла</td>
            <td><code>None</code></td>
            <td><code>Optional[str]</code></td>
        </tr>
        <tr>
            <td><code>package_type</code></td>
            <td>тип пакета файла</td>
            <td><code>None</code></td>
            <td><code>Optional[slinn.storage.PackageType]</code></td>
        </tr>
        <tr>
            <td><code>package_zip</code></td>
            <td>архив, в котором находится файл</td>
            <td><code>None</code></td>
            <td><code>Optional[str]</code></td>
        </tr>
        <tr>
            <td><code>io</code></td>
            <td>файловый поток</td>
            <td><code>None</code></td>
            <td><code>Optional[IO]</code></td>
        </tr>
    </tbody>
</table>

