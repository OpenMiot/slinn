from slinn.preprocessor import Preprocessor
from slinn import root, _
from slinn.tools.manage.command import Command
from slinn.tools.manage.colorcodes import *
from slinn.tools.manage.help_generator import help_generator
from slinn.tools.manage.misc import validate_name
from slinn.api import StorageApi
import sys
import os
import slinn
import shutil
import platform
import stat
import asyncio
import subprocess


root_command = Command()
pp = Preprocessor()
slinn_root = StorageApi(root)


@root_command.subcommand('init', ('path', 'name', 'slinn_location'))
async def create_command(path: str = '.', name: str = 'slinn_project', slinn_location: str | None = None):
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        print(f'{BLUE}{path} has already existed{RESET}')
    os.chdir(path)
    shutil.copyfile(f'{slinn.root}/defaults/project/ft_routing.py', 'ft_routing.py')
    shutil.copyfile(f'{slinn.root}/defaults/project/hc_routing.py', 'hc_routing.py')
    shutil.copyfile(f'{slinn.root}/defaults/project/slinn.toml', 'slinn.toml')
    with (
        open(f'{slinn.root}/defaults/project/pyproject.toml', 'r') as rfile,
        open('pyproject.toml', 'w') as wfile
    ):
        wfile.write(rfile.read().format(
            name = name,
            slinn_dep = 'slinn' + (f' @ {slinn_location}' if slinn_location else ' >= 3.0.0')
        ))
    
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = 'venv'
    await asyncio.to_thread(subprocess.run, ('uv', 'sync', '--active'), check = True, env = env)
    
    binaries_dir = 'venv\\Scripts' if platform.system() == 'Windows' else 'venv/bin'
    slinn_script_path = os.path.join(
        binaries_dir,
        'slinn' + ('.exe' if platform.system() == 'Windows' else '')
    )
    print(slinn_script_path, binaries_dir)
    with open('start.bat', 'w') as f:
        f.write(f'{slinn_script_path} run\r\n')
    with open('start.sh', 'w') as f:
        f.write(f'{slinn_script_path} run\n')
    os.chmod(
        'start.sh',
        stat.S_IMODE(os.lstat('start.sh').st_mode) | stat.S_IEXEC
    )
    print(f'{GREEN}Project has created{RESET}')
    try:
        shutil.copytree(f'{slinn.root}/templates/firstrun/', 'firstrun',
                        ignore=shutil.ignore_patterns('data'))
        shutil.copytree(f'{slinn.root}/templates/firstrun/data/', 'templates_data/firstrun')
        print(f'{GREEN}Template firstrun successfully installed{RESET}')
    except FileExistsError:
        print(f'{BLUE}Template firstrun has already existed installed{RESET}')
    except FileNotFoundError:
        print(f'{BLUE}Template firstrun not found{RESET}')

@root_command.subcommand('help')
async def help_command():
    print(help_generator('Slinn Admin', sys.argv[0], {
        'init path={project`s path} name={project`s name} slinn_location={location of slinn package}': 'create project',
        'help': 'display this message',
        'version': 'display slinn`s version',
    }))

@root_command.subcommand('version')
async def version_command():
    print(slinn.version)

@root_command.command_not_exists()
async def default_command():
    print(f'{RED}Command not exists{RESET}')

@root_command.command_not_specified()
async def command_not_specified():
    print(f'{RED}Command was not specified{RESET}')


def main():
    asyncio.run(root_command(sys.argv[1:]))

if __name__ == '__main__':
    main()