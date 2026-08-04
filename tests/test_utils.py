from slinn.utils import *
import pytest


def test_optional_base():
    def func(*args, **kwargs):
        return args, kwargs

    assert optional(
        func, 1, 2, 3, a = 4, b = 5, c = 6
    ) == ((1, 2, 3), {'a': 4, 'b': 5, 'c': 6})

def test_optional_alt():
    def func(a, b, c, d=4, e=5, f=6):
        return a, b, c, d, e, f

    assert optional(
        func, a = 4, b = 5, c = 6, d = 5, lolkek=4
    ) == (4, 5, 6, 5, 5, 6)

def test_optional_multiply_values():
    def func(a):
        return a

    with pytest.raises(TypeError):
        optional(func, 1, a=1)
