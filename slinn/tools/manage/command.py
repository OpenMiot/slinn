from __future__ import annotations
from functools import partial
from slinn.utils import optional
from .misc import get_args


class Command:
    def __init__(self, command: str='', func: callable=None, excepting: tuple[str, ...]=(), children: list|None=None) -> None:
        self.command = command
        self.func = func
        self.excepting = excepting
        self.children = children if children else []
        self.not_exists = None
        self.not_specified = None

    def subcommand(self, command: str, excepting: tuple[str, ...]=()) -> callable:
        def wrapper(func):
            self.children.append(Command(command, func=func, excepting=excepting))
            return func

        return wrapper

    def command_not_exists(self) -> callable:
        def wrapper(func):
            self.not_exists = func
            return func

        return wrapper

    def command_not_specified(self) -> callable:
        def wrapper(func):
            self.not_specified = func
            return func

        return wrapper

    def __call__(self, argv: str) -> callable:
        if not argv:
            return self.not_specified
        for child in self.children:
            if child.command == argv[0]:
                return partial(optional, child.func, args=get_args(list(child.excepting), ' '.join(argv[1:])))
        return self.not_exists
