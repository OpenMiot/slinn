from slinn.preprocessor import Preprocessor
from slinn import slinn_root
from slinn.tools.manage.command import Command
from slinn.tools.manage.colorcodes import *
from slinn.tools.manage.help_generator import help_generator
import venv
import sys
import os
import slinn
import shutil
import platform
import stat


root_command = Command()
pp = Preprocessor()


@root_command.subcommand('create-project', ('path', ))
def create_command(args: dict):
    def _install_scripts(scripts: dict[str, str], path: str):
        def _install_script(script: tuple[str, str]):
            if platform.system() == 'Windows':
                script_path = os.path.join(path, f'{script[0]}.bat')
                with open(script_path, 'w') as f:
                    f.write(f'@echo off\r\n{os.path.abspath(os.path.join(path, "python.exe"))} -m {script[1]} %* & call call\r\n')
            else:
                script_path = os.path.join(path, f'{script[0]}.sh')
                with open(script_path, 'w') as f:
                    f.write(f'#!/usr/bin/sh\n{os.path.abspath(os.path.join(path, "python"))} -m {script[1]} $*\n')
                os.chmod(script_path, os.stat(script_path).st_mode | (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        for script in scripts.items():
            _install_script(script)
    def _install_modules(modules: tuple[str, ...], path: str):
        def _install_module(name: str):
            try:
                shutil.copytree(
                    os.path.abspath(__import__(name).__file__).replace('__init__.py', ''),
                    path + f'/{name}',
                    dirs_exist_ok=True
                )
            except (FileNotFoundError, ModuleNotFoundError):
                print(f'{BLUE}{name} was not installed{RESET}')
        for module in modules:
            _install_module(module)
    apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
    if not os.path.isdir(apppath):
        os.mkdir(apppath)
    else:
        print(f'{BLUE}{apppath} has already existed{RESET}')
    shutil.copyfile(slinn.root + '/defaults/project/manage.py', f'{apppath}/manage.py')
    shutil.copyfile(slinn.root + '/defaults/project/htrf.py', f'{apppath}/htrf.py')
    shutil.copyfile(slinn.root + '/defaults/project/hcdp.py', f'{apppath}/hcdp.py')
    shutil.copyfile(slinn.root + '/defaults/project/project.json', f'{apppath}/project.json')
    venv.create(f'{apppath}/venv', with_pip=True)
    binaries_dir = f'{apppath}/venv/Scripts' \
                   if platform.system() == 'Windows' else \
                   f'{apppath}/venv/bin'
    packages_dir = f'{apppath}/venv/Lib/site-packages' \
                   if platform.system() == 'Windows' else \
                   f'{apppath}/venv/lib/python{".".join(sys.version.split(" ")[0].split(".")[:-1])}/site-packages'
    os.makedirs(packages_dir, exist_ok=True)
    _install_modules(
        ('slinn', 'dexir', 'wheel', 'setuptools'),
        packages_dir
    )
    _install_scripts(
        {
            'slinn-admin': 'slinn.scripts.slinn_admin',
            'slinn': 'slinn.scripts.slinn',
            'spm': 'slinn.scripts.spm'
        },
        binaries_dir
    )
    slinn_script_path = os.path.join(
        binaries_dir,
        '/slinn' + ('.bat' if platform.system() == 'Windows' else '')
    )
    with open(f'{apppath}/start.bat', 'w') as f:
        f.write(f'{slinn_script_path} run\r\n')
    with open(f'{apppath}/start.sh', 'w') as f:
        f.write(f'{slinn_script_path} run\n')
    os.chmod(
        f'{apppath}/start.sh',
        stat.S_IMODE(os.lstat(f'{apppath}/start.sh').st_mode) | stat.S_IEXEC
    )
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


@root_command.subcommand('update-project', ('path', ))
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
    print(help_generator('Slinn', sys.argv[0], {
        'create-project {project`s name}': 'create project',
        'update-project {project`s name}': 'update project',
        'help': 'display this message',
        'version': 'display slinn`s version',
    }))


@root_command.subcommand('version')
def version_command():
    print(slinn.version)


@root_command.command_not_exists()
def default_command():
    print(f'{RED}Command not exists{RESET}')


@root_command.command_not_specified()
def command_not_specified():
    print(f'{RED}Command was not specified{RESET}')


def main():
    root_command(sys.argv[1:])()

if __name__ == '__main__':
    main()