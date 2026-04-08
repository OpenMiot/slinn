from slinn.tools.manage.command import Command
from slinn.tools.manage.colorcodes import RED, RESET
import subprocess
import sys
import os


root_command = Command()


@root_command.command_not_exists()
@root_command.command_not_specified()
def default_command():
    if not os.path.isfile(os.path.join(os.getcwd(), 'manage.py')):
        print(f'{RED}Must be run in project`s root{RESET}')
        return
    try:
        subprocess.run(
            [sys.executable, 'manage.py'] + sys.argv[1:],
            cwd = os.getcwd()
        )
    except KeyboardInterrupt:
        ...

def main():
    root_command(sys.argv[1:])()

if __name__ == '__main__':
    main()