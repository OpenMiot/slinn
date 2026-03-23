from slinn.preprocessor import Preprocessor
from slinn import slinn_root
from .tools.manage.command import Command
from .tools.manage.colorcodes import *
import venv
import sys
import subprocess
import os
import slinn
import shutil
import platform
import stat


root_command = Command()
pp = Preprocessor()


@root_command.subcommand('create', ('path', ))
def create_command(args):
    apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
    if not os.path.isdir(apppath):
        os.mkdir(apppath)
    else:
        print(f'{BLUE}{apppath} has already existed{RESET}')
    shutil.copyfile(slinn.root + '/defaults/project/manage.py', f'{apppath}/manage.py')
    shutil.copyfile(slinn.root + '/defaults/project/htrf.py', f'{apppath}/htrf.py')
    shutil.copyfile(slinn.root + '/defaults/project/hcdp.py', f'{apppath}/hcdp.py')
    shutil.copyfile(slinn.root + '/defaults/project/project.json', f'{apppath}/project.json')
    with open(f'{apppath}/start.bat', 'w') as f:
        f.write(f'{sys.argv[0]} run\r\n')
    with open(f'{apppath}/start.sh', 'w') as f:
        executable = sys.argv[0].replace('\\', '/')
        f.write(f'{executable} run\n')
    os.chmod(
        f'{apppath}/start.sh',
        stat.S_IMODE(os.lstat(f'{apppath}/start.sh').st_mode) | stat.S_IEXEC
    )
    venv.create(f'{apppath}/venv', with_pip=True)
    binaries_dir = f'{apppath}/venv/Scripts' \
                   if platform.system() == 'Windows' else \
                   f'{apppath}/venv/bin'
    packages_dir = f'{apppath}/venv/Lib/site-packages' \
                   if platform.system() == 'Windows' else \
                   f'{apppath}/venv/lib/python{".".join(sys.version.split(" ")[0].split(".")[:-1])}/site-packages'
    try:
        os.makedirs(packages_dir, exist_ok=True)
    except FileExistsError:
        pass
    try:
        shutil.copytree(
            slinn.root,
            packages_dir + '/slinn',
            dirs_exist_ok=True
        )
        if platform.system() == 'Windows':
            scripts_dir = '/'.join(sys.argv[0].replace('\\', '/').split('/')[:-1])
            shutil.copyfile(
                scripts_dir + '/slinn.exe',
                binaries_dir + '/slinn.exe'
            )
            shutil.copyfile(
                scripts_dir + '/spm.exe',
                binaries_dir + '/spm.exe'
            )
    except Exception as e:
        return print(f'{RED}Cannot install slinn to the new virtual environment{RESET}')
    try:
        shutil.copytree(
            os.path.abspath(__import__('wheel').__file__).replace('__init__.py', ''),
            packages_dir + '/wheel',
            dirs_exist_ok=True
        )
    except (FileNotFoundError, ModuleNotFoundError):
        print(f'{BLUE}wheel was not installed{RESET}')
    try:
        shutil.copytree(
            os.path.abspath(__import__('setuptools').__file__).replace('__init__.py', ''),
            packages_dir + '/setuptools',
            dirs_exist_ok=True
        )
    except (FileNotFoundError, ModuleNotFoundError):
        print(f'{BLUE}setuptools was not installed{RESET}')
    print(f'{GREEN}Project has created{RESET}')
    try:
        shutil.copytree(f'{slinn.root}/templates/firstrun/', f'{apppath}/firstrun',
                        ignore=shutil.ignore_patterns('data'))
        shutil.copytree(f'{slinn.root}/templates/firstrun/data/', f'{apppath}/templates_data/firstrun')
        print(f'{GREEN}Template firstrun successfully installed{RESET}')
    except FileExistsError:
        print(f'{BLUE}Template firstrun has already existed installed{RESET}')
    except FileNotFoundError:
        print(f'{BLUE}Template firstrun not found{RESET}')


@root_command.subcommand('update', ('path', ))
def update_command(args):
    apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
    if not os.path.isdir(apppath):
        return print(f'{BLUE}`{apppath}` does not exist{RESET}')
    packages_dir = f'{apppath}/venv/Lib/site-packages' \
                   if platform.system() == 'Windows' else \
                   f'{apppath}/venv/lib/python{".".join(sys.version.split(" ")[0].split(".")[:-1])}/site-packages'
    if not os.path.isdir(packages_dir + '/slinn'):
        return print(f'{RED}Virtual environment directory is corrupted. Reinstall the project{RESET}')
    if not os.path.isfile(apppath + '/manage.py'):
        return print(f'{RED}manage.py file does not exist. Reinstall the project{RESET}')
    shutil.rmtree(packages_dir + '/slinn')
    os.remove(apppath + '/manage.py')
    shutil.copytree(slinn.root, packages_dir + '/slinn')
    shutil.copyfile(slinn.root + '/defaults/project/manage.py', f'{apppath}/manage.py')
    return print(f'{GREEN}Project has updated{RESET}')


@root_command.subcommand('help')
def help_command():
    with slinn_root('/tools/manage/module_main_help.template', 'r') as f:
        print(pp.preprocess(f.read(), {
            'cmd': f'py -m slinn',
            'gray': GRAY,
            'reset': RESET,
            'bold': BOLD
        }))


@root_command.subcommand('version')
def version_command():
    print(slinn.version)


@root_command.command_not_exists()
def default_command():
    try:
        subprocess.run([sys.executable, 'manage.py'] + sys.argv[1:])
    except KeyboardInterrupt:
        ...


@root_command.command_not_specified()
def command_not_specified():
    print(f'{RED}Command was not specified{RESET}')


def main():
    root_command(sys.argv[1:])()

if __name__ == '__main__':
    main()