from __future__ import annotations
from typing import Callable, Iterable, Generator, Optional
from .colorcodes import *
from .defaults import APP_CONFIG
from slinn import slinn_root, Migration
import os
import base64
import hashlib
import json
import glob
import importlib.util
import inspect
import sys
import zipfile
import fnmatch


def splits(string: str, delimiters=(' ', '\n'), quotes=tuple()):
    result = ['']
    current_quote = ''
    for char in str(string):
        if char in quotes:
            if current_quote == '':
                current_quote = char
                continue
            elif current_quote == char:
                current_quote = ''
                continue
        if current_quote == '':
            if char in delimiters:
                result.append('')
            else:
                result[-1] += char
        else:
            result[-1] += char
    return result


def get_args(expecting, text):
    text = text.strip()
    if text == '':
        return {}
    args = {'not_used': []}
    d_s = ('\n', ' ')
    q_s= ('"', "'", '`')
    spl_s = splits(text, d_s, q_s)
    i = 0
    while i < len(spl_s):
        arg = str(spl_s[i])
        try:
            if arg.strip().endswith('='):
                _w = arg.strip().removesuffix('=').strip()
                expecting.pop(expecting.index(_w))
                args[_w] = arg_parse(str(spl_s[i + 1]))
                i += 2
                continue
            if len(splits(arg, ['='], q_s)) == 2:
                spl = splits(arg, ['='])
                _w = str(spl[0])
                if _w not in args.keys():
                    args[_w] = arg_parse(str(spl[1]))
                    expecting.pop(expecting.index(_w))
                else:
                    args[_w] = [args[_w]]
                    args[_w].append(arg_parse(str(spl[1])))
                i += 1
                continue
        except ValueError:
            pass

        if len(expecting) == 0:
            args['not_used'].append(arg_parse(arg))
            i += 1
            continue

        E = expecting.pop(0)
        args[E] = arg_parse(arg)
        i += 1
    return args


def replace_all(text: str, sss: list[str]|str, ss2: str) -> str:
    for ss1 in sss:
        text = text.replace(ss1, ss2)
    return text


def get_dir_checksum(dir):
    def get_dir_checksums(dir):
        def md5(fname):
            hash_md5 = hashlib.md5()
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        paths = os.listdir(dir)
        checksums = []
        for path in paths:
            if os.path.isdir(path):
                checksums += get_dir_checksums(dir + '/' + path)
            elif path.endswith('.py'):
                checksums.append(path + md5(dir + '/' + path))
        return checksums

    return hashlib.md5(''.join([checksum for checksum in get_dir_checksums(dir)]).encode()).hexdigest()


def config():
    with slinn_root('/defaults/project/project.json', 'r') as f:
        cfg = json.load(f)
    with open('project.json') as f:
        cfg.update(json.load(f))
    return cfg


def packages():
    plg = {}
    with slinn_root('/defaults/project/spm_packages/packages.json', 'r') as f:
        plg = json.load(f)
    if os.path.isfile('spm_packages/packages.json'):
        with open('spm_packages/packages.json') as f:
            plg.update(json.load(f))
    return plg


def app_config(app):
    try:
        cfg = APP_CONFIG.copy()
        with open(f'{app}/config.json') as f:
            cfg.update(json.load(f))
        return cfg
    except FileNotFoundError:
        print(f'{RED}{app}/config.json file not found{RESET}')
        exit()


class MigrationMeta:
    def __init__(self, basename: str, cls: object):
        self.basename = basename
        self.cls = cls
        self.applied = False

    def set_applied(self):
        self.applied = True


def load_migration(path: str, package_name: Optional[str] = None) -> Generator[MigrationMeta, ...]:
    basename = os.path.basename(path)
    fullname = f'{package_name}.{basename}' if package_name else basename
    spec = importlib.util.spec_from_file_location(
        fullname,
        path
    )
    module = importlib.util.module_from_spec(spec)
    if package_name:
        # print(spec.parent, fullname.removesuffix('.py'))
        # spec.parent = package_name
        module.__package__ = package_name
        # module.__package__ = module.__spec__.parent
    sys.modules[fullname] = module
    spec.loader.exec_module(module)
    for key in module.__dict__:
        obj = getattr(module, key)
        if inspect.isclass(obj) and issubclass(obj, Migration) and not inspect.isabstract(obj):
            yield MigrationMeta(basename, obj)


def load_migrations(path_pattern: str, package_name: Optional[str] = None) -> Generator[MigrationMeta, ...]:
    for path in glob.glob(path_pattern):
        yield from load_migration(path, package_name)


def load_migrations_from_zip(path: str, package_name: Optional[str] = None) -> Generator[MigrationMeta, ...]:
    with zipfile.ZipFile(path, 'r') as zf:
        for path in [name for name in zf.namelist() if fnmatch.fnmatch(name, 'migrations/*.py')]:
            yield from load_migration(path, package_name)



arg_parse: Callable[[str], str] = lambda arg: (
    base64.urlsafe_b64decode(arg.removeprefix('b64@').encode() + b'==').decode() if arg.startswith('b64@') else arg)

add_quotes_to_list: Callable[[list[str]], Iterable] = lambda lst: (f'\'{l}\''for l in lst)

load_imports: Callable[[list[str], bool], list[str]] = lambda apps, plugins_zip, plugins_dir, debug=False: [
    f'import {app}' for app in apps if not app_config(app)['debug'] or debug
] + [
    f'sys.path.insert(0, "spm_packages/Plugins/{plugin_zip}.zip");import {plugin_zip}' for plugin_zip in plugins_zip
] + [
    f'sys.path.insert(0, "spm_packages/Plugins/{plugin_dir}");import {plugin_dir}' for plugin_dir in plugins_dir
]

get_dispatchers: Callable[[list[str], bool], list[str]] = lambda apps, plugins_zip, plugins_dir, debug=False: [
    f'{app}.dp' for app in apps if not app_config(app)['debug'] or debug
] + [
    f'{plugin_zip}.dp' for plugin_zip in plugins_zip | plugins_dir
]

app_reload : Callable[[str], str]= lambda app: f'global {app};{app} = importlib.reload({app});'
