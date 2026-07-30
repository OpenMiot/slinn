# SlinnAppAPI

Класс реализует интерфейс для взаимодействия со Slinn приложением

```Python
class SlinnAppAPI (
    path: str,
    package: Optional[str] = None
)
```

1. `path` - путь до приложения
2. `package` - пакет приложения

### Свойства

<table width="100%">
    <thead>
        <tr>
            <th width="20%">свойство</th>
            <th width="45%">описание</th>
            <th width="35%">тип</th>
        </tr>    
    </thead>
    <tbody>
        <tr>
            <td><code>config</code></td>
            <td>конфиг приложения (только геттер)</td>
            <td><code>dict</code></td>
        </tr>
    </tbody>
</table>
