from __future__ import annotations
from typing import Callable, Iterable, Generator, Optional
from .colorcodes import *
from .defaults import APP_CONFIG
from slinn import Migration, TemplateProtocol, root
from slinn.api.storage_api import StorageApi
import os
import base64
import hashlib
import tomlkit
import json
import glob
import importlib.util
import inspect
import sys
import zipfile
import fnmatch
import itertools


slinn_root = StorageApi(root)

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
    q_s = ('"', "'", '`')
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


def replace_all(text: str, sss: list[str] | str, ss2: str) -> str:
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
    with slinn_root('/defaults/project/slinn.toml', 'r') as f:
        cfg = tomlkit.load(f)
    with open('slinn.toml') as f:
        cfg.update(tomlkit.load(f))
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
        with open(f'{app}/config.toml', 'rb') as f:
            cfg.update(tomlkit.load(f))
        return cfg
    except FileNotFoundError:
        print(f'{RED}{app}/config.toml file not found{RESET}')
        exit()


class MigrationMeta:
    def __init__(self, basename: str, cls: object, package_key: str, is_zip: bool):
        self.basename = basename
        self.cls = cls
        self.package_key = package_key
        self.is_zip = is_zip
        self.display = f'{basename}@{package_key}'
        self.applied = False

    def set_applied(self):
        self.applied = True


def load_module(path: str, package_name: Optional[str] = None) -> object:
    basename = os.path.basename(path)
    fullname = f'{package_name}.{basename.removesuffix(".py")}' if package_name else basename
    spec = importlib.util.spec_from_file_location(
        fullname,
        path
    )
    module = importlib.util.module_from_spec(spec)
    if package_name:
        # print(spec.parent, fullname.removesuffix('.py'))
        # spec.parent = package_name
        # print(package_name)
        module.__package__ = package_name
        # module.__package__ = module.__spec__.parent
    sys.modules[fullname] = module
    spec.loader.exec_module(module)
    return module


def load_template(path: str, package_name: Optional[str] = None) -> TemplateProtocol:
    # TODO: stop using `load_module`

    module = load_module(path, package_name)
    for key in module.__dict__:
        obj = getattr(module, key)
        if inspect.isclass(obj) and issubclass(obj, TemplateProtocol) and not obj is TemplateProtocol:
            return obj


def load_migrations(package_path: str, package_key: str, is_zip: bool) -> Generator[MigrationMeta, ...]:
    imported_modules = set()

    def _load_migrations(internal_path: str):
        modname = internal_path \
            .removeprefix(package_path) \
            .replace('\\', '/') \
            .replace('/', '.') \
            .removeprefix('.') \
            .removesuffix('.py') \
            .removesuffix('.__init__')
        basename = os.path.basename(internal_path)
        module = importlib.import_module(modname)
        imported_modules.add(modname)
        for key in module.__dict__:
            obj = getattr(module, key)
            if (inspect.isclass(obj) and
                    issubclass(obj, Migration) and
                    not inspect.isabstract(obj)):
                yield MigrationMeta(basename, obj, package_key, is_zip)

    sys.path.insert(0, package_path)
    if is_zip:
        with zipfile.ZipFile(package_path, 'r') as zf:
            for internal_path in zf.namelist():
                if fnmatch.fnmatch(internal_path, 'migrations/*.py'):
                    yield from _load_migrations(internal_path)
    else:
        for internal_path in glob.glob(os.path.join(package_path, 'migrations/*.py')):
            yield from _load_migrations(internal_path)
    sys.path.pop(0)
    for imported_module in imported_modules:
        del sys.modules[imported_module]


def plugins_sorted(plugins, pkgs):
    _plugins = {}
    for key, plugin in plugins.items():
        for dependency in plugin.get('dependencies', []):
            if dependency.split('@')[0] in pkgs['plugins']:
                _plugins.update(plugins_sorted({
                    key: pkgs['plugins'][key]
                    for key in plugins
                    if key == dependency.split('@')[0]
                }, pkgs))
            else:
                print(f'{RED}Dependency {dependency.split("@")[0]} for {plugin["displayName"]} plugin is not resolved.{RESET}')
                print(f'Install it via {BOLD}Slinn Package Manager{RESET}:')
                print(f'  1. {GRAY}${RESET} {BOLD}spm update{RESET}')
                print(f'  2. {GRAY}${RESET} {BOLD}spm install {dependency}{RESET}')
                exit(1)
        _plugins[key] = plugin
    return _plugins


arg_parse: Callable[[str], str] = lambda arg: (
    base64.urlsafe_b64decode(arg.removeprefix('b64@').encode() + b'==').decode() if arg.startswith('b64@') else arg)

add_quotes_to_list: Callable[[list[str]], Iterable] = lambda lst: (f'\'{l}\'' for l in lst)

load_imports: Callable[[list[str], bool], list[str]] = lambda apps, plugins_zip, plugins_dir, debug=False: [
   f'sys.path.insert(0, "spm_packages/Plugins/{plugin_zip}.zip");import {plugin_zip};sys.path.pop(0)'
   for plugin_zip in plugins_zip
] + [
   f'sys.path.insert(0, "spm_packages/Plugins/{plugin_dir}");import {plugin_dir};sys.path.pop(0)'
   for plugin_dir in plugins_dir
] + [
   f'import {app}' for app in apps if not app_config(app)['debug'] or debug
]

get_routers: Callable[[list[str], bool], list[str]] = lambda apps, plugins_zip, plugins_dir, debug=False: [
  f'{app}.router' for app in apps if not app_config(app)['debug'] or debug
] + list(itertools.chain.from_iterable([
    [
        f'{key}.{router}' for router in plugin.get('plugin', {}).get('routers', [])
    ]
    for key, plugin in (plugins_zip | plugins_dir).items()
]))

app_reload: Callable[[str], str] = lambda app: f'global {app};{app} = importlib.reload({app});'
