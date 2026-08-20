from abc import ABCMeta
from typing import Any, Coroutine
from collections.abc import AsyncIterable
from slinn_cxx import representate
import warnings
import inspect
import datetime
import orjson
import re
import threading
import importlib
import importlib.util
import enum


def optional(func, *p, **k) -> Any:
    params = inspect.signature(func).parameters
    args, kwargs = [], {}
    for i, positional in enumerate(p):
        if i >= len(params):
            break
        match params[tuple(params)[i]].kind.name:
            case 'POSITIONAL_ONLY' | 'POSITIONAL_OR_KEYWORD':
                args.append(positional)
            case 'VAR_POSITIONAL':
                args.extend(p[i:])
                break
            case 'KEYWORD_ONLY' | 'VAR_KEYWORD': ...
    for i, keyword in enumerate(params):
        match params[tuple(params)[i]].kind.name:
            case 'KEYWORD_ONLY' | 'POSITIONAL_OR_KEYWORD':
                if keyword not in k:
                    continue
                kwargs[keyword] = k.get(keyword, None)
            case 'VAR_KEYWORD':
                kwargs.update(k)
                break
            case 'POSITIONAL_ONLY' | 'VAR_POSITIONAL': ...
    return func(*args, **kwargs)

def convert_datetime(dt: datetime.datetime) -> str:
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

class StoppableThread(threading.Thread):
    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def stopped(self) -> bool:
        return self._stop_event.is_set()


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


"""def representate(obj: Any) -> bytes:
    def __representate_str(obj: Any) -> str | dict | list | int | float | bool:
        if isinstance(obj, dict):
            return {key: __representate_str(obj[key]) for key in obj.keys()}
        if type(obj) in (list, tuple, set):
            return [__representate_str(elem) for elem in obj]
        if type(obj) in (str, int, float, bool):
            return obj
        if isinstance(obj, bytes):
            return obj.decode()
        if isinstance(obj, enum.Enum):
            return __representate_str(obj.value)
        if type(obj).__str__ != object.__str__ or type(obj).__repr__ != object.__repr__:
            try:
                return repr(obj)
            except Exception:
                pass
        try:
            return {key: __representate_str(obj.__dict__[key]) for key in obj.__dict__.keys()}
        except Exception as e:
            pass
        return f'<{type(obj)} object at {id(obj)}>'

    if type(obj) == bytes:
        return obj

    representated = __representate_str(obj)
    if type(representated) in (str, int, float, bool):
        return str(representated).encode()
    return orjson.dumps(representated)
"""
def wrap_in_quotes(text: str, open_quote='"', close_quote='"') -> str:
    return open_quote + text + close_quote
