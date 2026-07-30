# Preprocessor

Класс является универсальным текстовым препроцессором

```Python
class Preprocessor (
    open_quote: str = '<%',
    close_quote: str = '%>'
)
```

1. `open_quote` - открывающий тег
2. `close_quote` - закрывающий тег

### Методы

- `@staticmethod get_nested_value(obj: Any, key_path: str) -> Any` - возвращает значение из объекта по пути через точку;
- `replace_conditions(text: str, data: dict) -> str` - заменяет условные операторы:
    1. `text` - текст для препроцессинга;
    2. `data` - словарь с контекстом области видимости;
- `replace(text: str, data: dict) -> str` - генерирует все возможные конструкции (объекты, условия, циклы, макросы):
    1. `text` - текст для препроцессинга;
    2. `data` - словарь с контекстом области видимости;
- `preprocess(text: str, data: dict) -> str` - выполняет препроцессинг (генерирует + очищает от мусора):
    1. `text` - текст для препроцессинга;
    2. `data` - словарь с контекстом области видимости;
- `clean(text: str) -> str` - очищает текст от препроцессорных вставок:
    1. `text` - текст для очистки;
- `count(text: str) -> int` - считает количество препроцессорных вставок в тексте:
    1. `text` - текст для препроцессинга;
- `count_trash(text: str, data: dict) -> int` - считает количество неиспользованных препроцессорных вставок в тексте:
    1. `text` - текст для препроцессинга;
    2. `data` - словарь с контекстом области видимости.

### Примечания

`get_nested_value` рекурсивно обращается к полям объекта по пути, разделяя поля через символ точки `.`
```Python
from slinn import Preprocessor


user = {
    'id': 'mrybs',
    'full_name': 'Mark Radin',
    'photos': {
        'full_size': '/photos/mrybs/full_size.png',
        'thumbnails': {
            '256': '/photos/mrybs/thumbnail_256x256.png',
            '128': '/photos/mrybs/thumbnail_128x128.png',
            '32': '/photos/mrybs/thumbnail_32x32.png'
        }
    }
}


photo_path = Preprocessor.get_nested_value(
    user, 'photos.thumbnails.256'
)

print(photo_path)  # /photos/mrybs/thumbnail_256x256.png
```


Объекты из словаря с контекстом области видимости вывести в текст можно с помощью конструкции вида
`ОТКРЫВАЮЩИЙ-ТЕГ НАЗВАНИЕ-ОБЪЕКТА ЗАКРЫВАЮЩИЙ-ТЕГ`
```Python
pp = Preprocessor()

preprocessed1 = pp.preprocess(
    '''Hello, <% user.full_name %>!''',
    {
        'user': user
    }
)

print(preprocessed1)  # Hello, Mark Radin!
```

Условные конструкции используют синтаксис вида
`ОТКРЫВАЮЩИЙ-ТЕГ if ОБЪЕКТ ЗАКРЫВАЮЩИЙ-ТЕГ ТЕКСТ-ВЫВОДЯЩИЙСЯ-ПРИ-ВЫПОЛНЕНИИ-УСЛОВИЯ ОТКРЫВАЮЩИЙ-ТЕГ endif ЗАКРЫВАЮЩИЙ-ТЕГ`
```Python
preprocessed2 = pp.preprocess(
    '''
        <% if morning %>
            Good morning, <% user.full_name %>!
        <% endif %>
        <% if afternoon %>
            Good afternoon, <% user.full_name %>!
        <% endif %>
    ''',
    {
        'user': user,
        'morning': True,
        'afternoon': False
    }
)

print(preprocessed2)  # Good morning, Mark Radin!
```

Циклические конструкции используют синтаксис вида
`ОТКРЫВАЮЩИЙ-ТЕГ for ИТЕРАТОР in ИТЕРИРУЕМЫЙ-ОБЪЕКТ ЗАКРЫВАЮЩИЙ-ТЕГ ТЕКСТ-ВЫВОДЯЩИЙСЯ-ПРИ-КАЖДОЙ-ИТЕРАЦИИ ОТКРЫВАЮЩИЙ-ТЕГ end ЗАКРЫВАЮЩИЙ-ТЕГ`
```Python
preprocessed3 = pp.preprocess(
    '''
        <% for user in users %>
            Hi, <% user.name %>!
        <% end %>
    ''',
    {
        'users': {
            {
                'id': '001kpp',
                'name': 'Alikhan Kuchmenov'
            },
            {
                'id': 'modiant',
                'Gleb Kazantsev'
            }
        }
    }
)

print(preprocessed3)  # Hi, Alikhan Kuchmenov! Hi, Gleb Kazantsev!
```

Макросы используют синтаксис вида `ОТКРЫВАЮЩИЙ-ТЕГ МАКРОС ОБЪЕКТ ЗАКРЫВАЮЩИЙ-ТЕГ`
```Python
preprocessed4 = pp.preprocess(
    '''
        <% htmlsafe doc %>
    ''',
    {
        'doc': '<p>Hello, world!</p>',
    }
)

print(preprocessed4)  # &lt;p&gt;Hello, world!&lt;/p&gt;
```

Всего существует три макроса:

- `htmlsafe` - экранирует строку и делает ее безопасной для вывода в html файл
- `urlsafe` - экранирует строку и делает ее безопасной для использования в качестве аргумента ссылки
- `import` - выводит содержимое указанного файла
