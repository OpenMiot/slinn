from slinn.tools.manage.command import Command
import subprocess
import sys


root_command = Command()


@root_command.command_not_exists()
@root_command.command_not_specified()
def default_command():
    try:
        subprocess.run([sys.executable, 'manage.py'] + sys.argv[1:])
    except KeyboardInterrupt:
        ...

def main():
    root_command(sys.argv[1:])()

if __name__ == '__main__':
    main()