import venv
import sys
import subprocess
from .default import *


RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'
RESET = '\u001b[0m'
BOLD = '\u001b[1m'
GRAY = '\u001b[38;2;127;127;127m'


if __name__ == '__main__':
    main()

def main():
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'create':
            args = get_args(['path'], ' '.join(sys.argv[2:]))
            apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
            import os, slinn, shutil, platform

            modulepath = os.path.abspath(slinn.__file__).replace('__init__.py', '')
            if not os.path.isdir(apppath):
                os.mkdir(apppath)
            else:
                print(f'{BLUE}{apppath} has already existed{RESET}')
            shutil.copyfile(modulepath + 'default/manage.py', f'{apppath}/manage.py')
            shutil.copyfile(modulepath + 'default/htrf.py', f'{apppath}/htrf.py')
            shutil.copyfile(modulepath + 'default/project.json', f'{apppath}/project.json')
            venv.create(f'{apppath}/venv')
            packages_dir = ''
            if platform.system() == 'Windows':
                packages_dir = f'{apppath}/venv/Lib/site-packages'
            else:
                packages_dir = f'{apppath}/venv/lib/python{".".join(sys.version.split(" ")[0].split(".")[:-1])}/site-packages'
            try:
                os.makedirs(packages_dir)
            except FileExistsError:
                pass
            try:
                shutil.copytree(modulepath, packages_dir + '/slinn')
            except FileNotFoundError:
                print(f'{RED}Cannot install slinn to the new virtual environment{RESET}')
                exit()
            try:
                shutil.copytree(os.path.abspath(__import__('pip').__file__).replace('__init__.py', ''), packages_dir + '/pip')
            except FileNotFoundError:
                print(f'{BLUE}pip was not installed{RESET}')
            try:
                shutil.copytree((os.path.abspath(__import__('wheel').__file__).replace('__init__.py', '')).decode(), packages_dir + '/wheel')
            except Exception:
                print(f'{BLUE}wheel was not installed{RESET}')
            try:
                shutil.copytree(os.path.abspath(__import__('setuptools').__file__).replace('__init__.py', ''), packages_dir + '/setuptools')
            except Exception:
                print(f'{BLUE}setuptools was not installed{RESET}')
            print(f'{GREEN}Project has created{RESET}')
            modulepath = os.path.abspath(slinn.__file__).replace('__init__.py', '')
            try:
                shutil.copytree(f'{modulepath}templates/firstrun/', f'{apppath}/firstrun')
                shutil.copytree(f'{modulepath}templates/firstrun/data/', f'{apppath}/templates_data/firstrun')
                print(f'{GREEN}Template firstrun successfully installed{RESET}')
            except FileExistsError:
                print(f'{BLUE}Template firstrun has already existed installed{RESET}')
            except FileNotFoundError:
                print(f'{BLUE}Template firstrun not found{RESET}')
        elif sys.argv[1].lower() == 'update':
            args = get_args(['path'], ' '.join(sys.argv[2:]))
            apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
            import os, slinn, shutil, platform

            modulepath = os.path.abspath(slinn.__file__).replace('__init__.py', '')
            if not os.path.isdir(apppath):
                print(f'{BLUE}`{apppath}` does not exist{RESET}')
                exit()
            packages_dir = ''
            if platform.system() == 'Windows':
                packages_dir = f'{apppath}/venv/Lib/site-packages'
            else:
                packages_dir = f'{apppath}/venv/lib/python{".".join(sys.version.split(" ")[0].split(".")[:-1])}/site-packages'
            if not os.path.isdir(packages_dir + '/slinn'):
                print(f'{RED}Virtual environment directory is corrupted. Reinstall the project{RESET}')
                exit()
            if not os.path.isfile(apppath + '/manage.py'):
                print(f'{RED}manage.py file does not exist. Reinstall the project{RESET}')
                exit()
            shutil.rmtree(packages_dir + '/slinn')
            os.remove(apppath + '/manage.py')
            shutil.copytree(modulepath, packages_dir + '/slinn')
            shutil.copyfile(modulepath + 'default/manage.py', f'{apppath}/manage.py')
            print(f'{GREEN}Project has updated{RESET}')
        elif sys.argv[1].lower() == 'help':
            print("""%BOLD%Slinn help page

Commands%RESET%:
	%cmd% create {project`s name}		%GRAY%# Creates a new project%RESET%
	%cmd% update {project`s name}		%GRAY%# Updates the project%RESET%
	%cmd% help                   		%GRAY%# Prints this help%RESET%
	%cmd% version                		%GRAY%# Prints version of Slinn%RESET%
""".replace('%cmd%', f'py -m slinn').replace('%GRAY%', GRAY).replace('%RESET%', RESET).replace('%BOLD%', BOLD))
        elif sys.argv[1].lower() == 'version':
            print(slinn.version)
        else:
            #print(f'{RED}Command {sys.argv[1].lower()} is not exists{RESET}')
            subprocess.run([sys.executable, 'manage.py'] + sys.argv[1:])
    else:
        print(f'{RED}Command was not specified{RESET}')
