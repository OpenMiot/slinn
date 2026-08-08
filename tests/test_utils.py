import pytest

from slinn.utils import *


def describe_optional():
    def var():
        def func(*args, **kwargs):
            return args, kwargs

        assert optional(
            func, 1, 2, 3, a = 4, b = 5, c = 6
        ) == ((1, 2, 3), {'a': 4, 'b': 5, 'c': 6})

    def base():
        def func(a, b, c, d=4, e=5, f=6):
            return a, b, c, d, e, f

        assert optional(
            func, a = 4, b = 5, c = 6, d = 5, lolkek=4
        ) == (4, 5, 6, 5, 5, 6)

    def multiply_values():
        def func(a):
            return a

        with pytest.raises(TypeError):
            optional(func, 1, a=1)

    def unused_keys():
        def func(*, a):
            return a

        optional(
            func, a = 1, b = 2
        )

    def keyword_only():
        def func(*, a):
            return a

        with pytest.raises(TypeError):
            optional(
                func, 1
            )


def describe_representation():
    def base():
        assert representate({
            'user': {
                'id': 1,
                'name': 'mrybs',
                'display_name': b'Mark',
                'is_banned': False,
                'age': 16.95,
                'flags': {'admin', 'op'},
                'friends': ['001kpp', 'modiant', 'wish'],
                'locale': ('ru', 'RU')
            }
        }) in (
            (b'{"user":{"id":1,"name":"mrybs","display_name":"Mark","is_banned":false,"age":16.95,'
             b'"flags":["admin","op"],"friends":["001kpp","modiant","wish"],"locale":["ru","RU"]}}'),
            (b'{"user":{"id":1,"name":"mrybs","display_name":"Mark","is_banned":false,"age":16.95,'
             b'"flags":["op","admin"],"friends":["001kpp","modiant","wish"],"locale":["ru","RU"]}}')
        )

    def non_unicode():
        assert representate(b'\x81') == b'\x81'