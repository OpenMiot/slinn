import warnings
import inspect
import json
import re
import threading
from abc import ABCMeta
from typing import Any


optional = lambda func, *a, **w: func(*a, **{k: v for k, v in w.items() if k in inspect.signature(func).parameters})
rematcheswith = lambda text, reg: re.match('^' + reg + '$', text) is not None


class StoppableThread(threading.Thread):
    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def stopped(self) -> bool:
        return self._stop_event.is_set()


def make_deprecated(obj, what_instead):
    class Wrapper(obj):
        __is_deprecation_warned = False
        
        def __init__(self, *args, **kwargs):
            if not Wrapper.__is_deprecation_warned:
                warnings.warn(f"Using {obj.__name__} is deprecated. Instead of use {what_instead.__name__}", DeprecationWarning, stacklevel=256)
            Wrapper.__is_deprecation_warned = True
            super().__init__(*args, **kwargs)
    return Wrapper


def restartswith(text: str, reg: str) -> bool:
    buf, largest = '', None
    for c in text:
        buf += c
        if re.sub(reg, '', buf) == '':
            largest = buf
    return largest is not None


def Bmin_restartswith_size(text: str, reg: str) -> int:
    buf, smallest = text, None
    for _ in range(len(text)):
        buf = buf[:-1]
        if re.sub(reg, '', buf) == '':
            smallest = buf
        else:
            break
    return len(smallest) if smallest is not None else 2147483647


def min_restartswith_size(text: str, reg: str) -> int:
    buf, smallest = text, None
    for _ in range(len(text)):
        buf = buf[:-1]
        if re.sub(reg, '', buf) == '':
            smallest = buf
    return len(smallest) if smallest is not None else 2147483647


def representate(obj: Any) -> bytes:
    if type(obj) == dict:
        return json.dumps({key:representate(obj[key]).decode() for key in obj.keys()}, ensure_ascii=False).encode()
    if type(obj) in [list, tuple, set]:
        return b', '.join([representate(elem) for elem in obj])
    if type(obj) == str:
        return obj.encode()
    if type(obj) == bytes:
        return obj
    if type(obj) in [int, float]:
        return str(obj).encode()
    if type(obj) == bool:
        return b'true' if obj else b'false'
    if type(obj).__str__ != object.__str__ or type(obj).__repr__ != object.__repr__:
        try: return str(obj).encode()
        except Exception: pass
    try: return json.dumps({key:representate(obj.__dict__[key]).decode() for key in obj.__dict__.keys()}, ensure_ascii=False).encode()
    except Exception as e: print(e)
    return f'<{type(obj)} object at {id(obj)}>'


def __representate_str(obj: any) -> str | dict | list | int | float | bool:
    if isinstance(obj, dict):
        return {key: __representate_str(obj[key]) for key in obj.keys()}
    if type(obj) in (list, tuple, set):
        return [__representate_str(elem) for elem in obj]
    if type(obj) in (str, int, float, bool):
        return obj
    if isinstance(obj, bytes):
        return obj.decode()
    if type(obj).__str__ != object.__str__ or type(obj).__repr__ != object.__repr__:
        try:
            return repr(obj)
        except Exception:
            pass
    try:
        return json.dumps({key: __representate_str(obj.__dict__[key]) for key in obj.__dict__.keys()}, ensure_ascii=False)
    except Exception as e:
        pass
    return f'<{type(obj)} object at {id(obj)}>'


def representate_str(obj: any) -> str:
    try:
        return json.dumps(__representate_str(obj), ensure_ascii=False)
    except:
        return __representate_str(obj)


def rename_class(cls, name):
    new = type(cls)(
        name,
        cls.__bases__,
        dict(cls.__dict__)
    )
    new.__qualname__ = new.__qualname__.replace(cls.__name__, name)
    new.__name__ = name
    return new
