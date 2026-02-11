from __future__ import annotations
from . import Filter, utils

class MagicMeta(type):
    """Метакласс, который переопределяет все магические методы."""

    def __new__(cls, name, bases, dct):
        # Список магических методов для перехвата
        magic_methods = ('__cmp__', '__eq__', '__ne__', '__lt__', '__gt__', '__le__', '__ge__',
                         '__pos__', '__neg__', '__abs__', '__invert__', '__round__', '__floor__',
                         '__ceil__', '__trunc__', '__add__', '__sub__', '__mul__', '__floordiv__',
                         '__div__', '__truediv__', '__mod__', '__divmod__', '__pow__', '__lshift__',
                         '__rshift__', '__and__', '__or__', '__xor__', '__radd__', '__rsub__', '__rmul__',
                         '__rfloordiv__', '__rdiv__', '__rtruediv__', '__rmod__', '__rdivmod__', '__rpow__',
                         '__rlshift__', '__rrshift__', '__rand__', '__ror__', '__rxor__', '__iadd__',
                         '__isub__', '__imul__', '__ifloordiv__', '__idiv__', '__itruediv__', '__imod__',
                         '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ior__', '__ixor__',
                         '__int__', '__long__', '__float__', '__complex__', '__oct__', '__hex__',
                         '__index__', '__coerce__', '__str__', '__repr__', '__unicode__',
                         '__format__', '__hash__', '__nonzero__', '__dir__', '__sizeof__',
                         '__len__', '__getitem__', '__setitem__', '__delitem__',
                         '__iter__', '__reversed__', '__contains__', '__missing__', '__instancecheck__',
                         '__subclasscheck__', '__call__', '__enter__', '__exit__', '__get__', '__set__',
                         '__delete__', '__copy__', '__deepcopy__', '__getinitargs__', '__getnewargs__',
                         '__getstate__', '__setstate__', '__reduce__', '__reduce_ex__', '__bytes__',
                         '__bool__')

        default_results = {
            '__contains__': False,
            '__bool__': False
        }

        def create_wrapper(method_name, res):
            def wrapper(self, *args, **kwargs):
                # Записываем вызов в историю
                self._stacktrace.append((method_name, args, kwargs))
                # Возвращаем новый MagicObject для цепочки вызовов
                return MagicObject(super_=self) if res is None else res

            return wrapper

        # Динамически добавляем обертки для методов
        for method in magic_methods:
            if method in dct:
                continue  # Не переопределяем если уже есть
            dct[method] = create_wrapper(method, default_results.get(method, None))
        return super().__new__(cls, name, bases, dct)


class MagicObject(Filter, metaclass=MagicMeta):
    def __init__(self, super_=None):
        # Используем object.__setattr__ чтобы избежать рекурсии
        object.__setattr__(self, 'super_', super_)
        object.__setattr__(self, '_stacktrace', [])
        # Вызываем родительский конструктор
        super().__init__('')

    def __getattribute__(self, name):
        # Обрабатываем только обычные атрибуты, не служебные
        if name in ['super_', '_stacktrace', 'check']:
            return object.__getattribute__(self, name)

        # Для всех остальных атрибутов добавляем в историю
        stacktrace = object.__getattribute__(self, '_stacktrace')
        stacktrace.append(('__getattr__', (name,), {}))
        return MagicObject(super_=self)

    def __setattr__(self, name, value):
        if name in ['super_', '_stacktrace']:
            object.__setattr__(self, name, value)
        else:
            stacktrace = object.__getattribute__(self, '_stacktrace')
            stacktrace.append(('__setattr__', (name, value), {}))

    def check(self, target_obj):
        """Применяет записанные операции к целевому объекту."""
        print('c2', target_obj)
        print(target_obj.__dict__)
        current = target_obj

        for op in self._stacktrace:
            method_name, args, kwargs = op

            try:
                if method_name == '__getattr__':
                    # Для получения атрибута
                    attr_name = args[0]
                    if hasattr(current, attr_name):
                        current = getattr(current, attr_name)
                    else:
                        return False
                elif method_name == '__setattr__':
                    # Для установки атрибута - пропускаем при проверке
                    continue
                else:
                    # Для всех остальных методов
                    if hasattr(current, method_name):
                        method = getattr(current, method_name)
                        current = method(*args, **kwargs)
                    else:
                        return False
            except Exception:
                return False

        return current

    def size(self, request: Request) -> int:
        if not self.check(request):
            return -1
        return 2147483647
