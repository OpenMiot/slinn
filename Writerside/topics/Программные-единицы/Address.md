# Address

Структура адреса TCP/IP сокета с разрешением доменных имен

```Python
class slinn.Address (
    port: int,
    host: Optional[str] = None
)
```

1. `port` - TCP-порт адреса сокета;
2. `host` - доменное имя адреса сокета или IP-адрес сокета.

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
            <td><code>port</code></td>
            <td>TCP-порт адреса сокета</td>
            <td></td>
            <td><code>int</code></td>
        </tr>
        <tr>
            <td><code>host</code></td>
            <td>IP-адрес сокета</td>
            <td><code>''</code></td>
            <td><code>str</code></td>
        </tr>
        <tr>
            <td><code>domain</code></td>
            <td>доменное имя адреса сокета</td>
            <td><code>''</code></td>
            <td><code>str</code></td>
        </tr>
    </tbody>
</table>
