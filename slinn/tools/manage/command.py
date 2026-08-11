from __future__ import annotations
from typing import Callable, Optional, Iterable, Awaitable
from types import AsyncGeneratorType
from slinn.tools.manage.colorcodes import RESET
from slinn.utils import optional
from .misc import get_args
import inspect
import functools


class Command:
    def __init__(
        self,
        command: str = '',
        func: Optional[Callable] = None,
        excepting: Iterable[str] = (),
        children: Optional[list] = None
    ) -> None:
        self.command = command
        self.func = func
        self.excepting = excepting
        self.children = children if children else []
        self.not_exists: Awaitable = None
        self.not_specified: Awaitable = None

    def subcommand(self, command: str, excepting: Iterable[str] = ()) -> Callable:
        def decorator(func) -> Callable:
            self.children.append(Command(command, func=func, excepting=excepting))
            return func

        return decorator

    def command_not_exists(self) -> Callable:
        def decorator(func) -> Callable:
            self.not_exists = func
            return func

        return decorator

    def command_not_specified(self) -> Callable:
        def decorator(func) -> Callable:
            self.not_specified = func
            return func

        return decorator

    async def __call__(self, argv: list[str]):
        if not argv:
            return await self._print_func(self.not_specified())
        for child in self.children:
            if child.command == argv[0]:
                if inspect.isasyncgenfunction(child.func):
                    @functools.wraps(child.func)
                    async def func(*args, **kwargs):
                        async for res in optional(
                            child.func,
                            **get_args(list(child.excepting), ' '.join(argv[1:]))
                        ):
                            yield res
                    return await self._print_func(func())
                else:
                    return await self._print_func(optional(
                        child.func,
                        **get_args(list(child.excepting), ' '.join(argv[1:]))
                    ))
        return await self._print_func(self.not_exists())

    async def _print_func(self, func):
        if isinstance(func, AsyncGeneratorType):
            async for message in func:
                self._print_message(message)
        else:
            if message := await func:
                self._print_message(message)

    def _print_message(self, message):
        if type(message) is tuple:
            if len(message) == 2:
                if message[1]:
                    print(message[1] + str(message[0]) + RESET)
                else:
                    print(message[0], end='')
        else:
            print(message)
