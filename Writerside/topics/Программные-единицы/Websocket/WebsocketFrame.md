# WebSocketFrame

Объект класса является представлением Websocket фрейма

```Python
class WebSocketFrame (
    final: bool,
    opcode: slinn.WebSocketOpcodes,
    mask: bool,
    payload: bytes,
    masking_key: Optional[bytes] = None
)
```

1. `final` - является ли фрейм последним;
2. `opcode` - код операции фрейма;
3. `mask` - используется ли маскирование;
4. `payload` - полезная нагрузка;
5. `masking_key` - бинарная маска полезной нагрузки.

### Методы

- `@staticmethod mask_payload(payload: bytes, masking_key: bytes) -> Iterator[int]` - маскирует полезную нагрузку;
    1. `payload` - полезная нагрузка;
    2. `masking_key` - бинарная маска полезной нагрузки;
- `@staticmethod pack(frame: WebSocketFrame) -> bytes` - сериализует фрейм
    1. `frame` - фрейм
- `@staticmethod unpack(data: bytes) -> WebSocketFrame` - десериализует фрейм
    1. `data` - сериализованный фрейм
- `@staticmethod _sock_read(recv)`

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
            <td><code>final</code></td>
            <td>является ли фрейм последним</td>
            <td></td>
            <td><code>bool</code></td>
        </tr>
        <tr>
            <td><code>opcode</code></td>
            <td>код операции фрейма</td>
            <td></td>
            <td><code>slinn.WebSocketOpcodes</code></td>
        </tr>
        <tr>
            <td><code>mask</code></td>
            <td>используется ли маскирование</td>
            <td></td>
            <td><code>bool</code></td>
        </tr>
        <tr>
            <td><code>masking_key</code></td>
            <td>бинарная маска полезной нагрузки</td>
            <td><code>None</code></td>
            <td><code>Optional[bytes]</code></td>
        </tr>
        <tr>
            <td><code>payload</code></td>
            <td>полезная нагрузка</td>
            <td></td>
            <td><code>bytes</code></td>
        </tr>
    </tbody>
</table>
