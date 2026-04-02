from .colorcodes import *


def help_generator(name: str, root: str, commands: dict) -> str:
    return (
        f'{BOLD}{name}{RESET}\n\n'
        f'{CYAN}Usage{RESET}:\n'
        f'  {root} <command>\n\n'
        f'{CYAN}Commands{RESET}:\n') + '\n'.join(
            [
                f'  {BOLD}{name.ljust(max(map(len, commands)) + 2)}{RESET}{desc.capitalize()}.'
                for name, desc in commands.items()
            ]
        )
