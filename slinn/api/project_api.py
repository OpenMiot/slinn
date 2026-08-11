from slinn import root, Preprocessor, _, Dispatcher
from slinn.tools.manage.misc import (
    replace_all, add_quotes_to_list, packages, load_module, load_imports,
    load_migrations, plugins_sorted, load_template, validate_name
)
from slinn.tools.manage.colorcodes import *
from slinn.net.address import AddressConfigFactory
from slinn.tools.manage.defaults import APP_CONFIG
from slinn.api.exceptions import AppExistsException, AppNotExistException, AppNameIsNotSpecified, AppNameIsNotValid
from slinn.net import RouterProtocol
from slinn.api import AppApi, StorageApi
from typing import Optional, Iterator
from pydantic import BaseModel
import logging
import os
import tomlkit
import tomlkit.items
import shutil
import sys
import slinn


slinn_root = StorageApi(root)
pp = Preprocessor()


class ProjectConfig(BaseModel):
    class Project(BaseModel):
        name: str
        display_name: str
        version: str = '1.0.0'
        description: str = ''
        debug: bool = False
    project: Project

    class Address(BaseModel):
        name: str
        port: str
        host: str
        domains: list[str]
        protocol: str
        tls: bool = False
    addresses: list[Address] = []

    class App(BaseModel):
        name: str
        enabled: bool = True
        debug_only: bool = False
        portmap: dict = {}
    apps: list[App] = []

    class TLS(BaseModel):
        default_fullchain: bool | str = False
        default_privkey: bool | str = False
    tls: Optional[TLS]

    class Protocol(BaseModel):
        class TCP(BaseModel):
            timeout: float = 0.5
            max_timeout: float = 60
            max_bytes_per_receive: int = 65535
        tcp: Optional[TCP] = TCP()

        class HTTP(BaseModel):
            max_header_size: int = 8192
        http: Optional[HTTP] = HTTP()

        class WebSocket(BaseModel):
            max_frame_size: int = 65535
            ping_interval: float = 30
        websocket: Optional[WebSocket] = WebSocket()

        class QUIC(BaseModel):
            idle_timeout: float = 60
        quic: Optional[QUIC] = QUIC()
    protocols: Protocol = Protocol()

    class Logging(BaseModel):
        level: str = 'info'
        format: str = 'text'
        output: str = 'stdout'
    logging: Optional[Logging]


class ProjectApi:
    def __init__(self, path: str):
        self.path = path
        self.storage = StorageApi(path)
        self.config: ProjectConfig = None

    def run(self):
        pkgs = packages()
        pkgs['plugins'] = plugins_sorted(pkgs['plugins'], pkgs)

        routers = list(*app.load_routers() for app in self.load_apps())
        if not routers:
            yield _('Routers not found. Check your apps, packages and ./project.json'), RED
            return

        yield GRAY, False
        if self.config.apps:
            yield _('Apps: {apps}').format(apps=', '.join([
                app.name if not app.debug_only or self.config.project.debug else f'[{STRIKE}{app.name}{NONSTRIKE}]'
                for app in self.config.apps
            ]))
        if pkgs['plugins']:
            yield _('Plugins: {plugins}').format(plugins=', '.join([
                plugin['displayName'] if plugin['enabled'] else f'[{STRIKE}{plugin['displayName']}{NONSTRIKE}]'
                for plugin in pkgs['plugins'].values()
            ]))
        yield _('Debug mode {status}').format(status=_('enabled') if self.config.project.debug else _('disabled'))
        yield RESET
        yield _('Starting server...')

        # logging.basicConfig(filename=f'{cfg.project.name}.journal.log', level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        addresses = {}
        for address in self.config.addresses:
            addresses[address.name] = AddressConfigFactory.get_address(**address.model_dump())
        for app in self.config.apps:
            for port, address_name in app.portmap:
                ...
        dispatcher = Dispatcher(
            addresses=addresses.values(),
            routers=routers,
            protocols_config=self.config.protocols.model_dump(),
            logger=logging.getLogger(self.config.project.name)
        )

        dispatcher.start()
        dispatcher.print_servers()
        yield _('Press CTRL+C to quit'), BOLD
        dispatcher.join()

    def load_config(self):
        with self.storage('slinn.toml', 'r') as rfile:
            self.config = ProjectConfig(**tomlkit.loads(rfile.read().replace('\r', '')))

    def save_config(self):
        def _deep_update(mapping, updates):
            if isinstance(mapping, (list, tomlkit.items.AoT)) and isinstance(updates, list):
                for i, item in enumerate(updates):
                    if i < len(mapping):
                        if isinstance(item, dict):
                            _deep_update(mapping[i], item)
                        else:
                            mapping[i] = item
                    else:
                        if isinstance(item, dict):
                            new_table = tomlkit.table()
                            _deep_update(new_table, item)
                            mapping.append(new_table)
                        else:
                            mapping.append(item)
                while len(mapping) > len(updates):
                    mapping.pop()
                return mapping

            for key, value in updates.items():
                if key in ('portmap', ) and isinstance(value, dict):
                    inline_table = tomlkit.inline_table()
                    inline_table.update(value)
                    mapping[key] = inline_table
                    continue

                current_val = mapping.get(key)
                if isinstance(value, dict) and isinstance(current_val,
                                                          (dict, tomlkit.items.Table, tomlkit.TOMLDocument)):
                    _deep_update(current_val, value)
                elif isinstance(value, list) and isinstance(current_val, (list, tomlkit.items.AoT)):
                    _deep_update(current_val, value)
                else:
                    mapping[key] = value
            return mapping

        toml_config: tomlkit.TOMLDocument = None
        with self.storage('slinn.toml', 'r') as rfile:
            toml_config = tomlkit.loads(rfile.read().replace('\r', ''))
        new_config = self.config.model_dump()
        with self.storage('slinn.toml', 'w') as wfile:
            wfile.write(tomlkit.dumps(_deep_update(toml_config, new_config)).replace('\r', ''))

    def load_apps(self) -> Iterator[AppApi]:
        for app in self.config.apps:
            if (app.debug_only and not self.config.project.debug) or not os.path.isdir(app.name):
                continue
            app_api = AppApi(app.name, self)
            app_api.load_config()
            yield app_api

        # routers = get_routers([app['name'] for app in cfg['apps']], plugins_zip, plugins_dir, cfg.get('debug', False))

    def create_app(self, name: str, *, init: bool = True) -> None:
        if not name:
            raise AppNameIsNotSpecified()
        if not validate_name(name):
            raise AppNameIsNotValid(name)
        if os.path.isdir(name):
            raise AppExistsException(name)

        app_storage = self.storage.substorage(name)
        if init:
            with (app_storage('__init__.py', 'w') as wfile,
                  slinn_root('/defaults/app/__init__.template.py', 'r') as rfile):
                wfile.write(rfile.read().format(name=name))
            with (app_storage('app.py', 'w') as wfile,
                  slinn_root('/defaults/app/app.template.py', 'r') as rfile):
                wfile.write(rfile.read())
            with (app_storage('config.toml', 'w') as wfile,
                  slinn_root('/defaults/app/config.template.toml', 'r') as rfile):
                wfile.write(rfile.read())

        self.config.apps.append(ProjectConfig.App(name=name))
        self.save_config()

    @staticmethod
    def create_app_from_template(name: str, template_name: str, path: str = '.',
                                 templates_folder=slinn.root + '/templates') -> None:
        apppath = (path + '?').replace('/?', '').replace('?', '')
        config = ProjectAPI.get_config()
        if name in config['apps']:
            raise AppExistsException(name)
        config['apps'].insert(0, name)
        with open('project.json', 'w') as project:
            json.dump(config, project, indent=4)
        try:
            shutil.copytree(f'{templates_folder}/{template_name}/', f'{apppath}/{name}',
                            ignore=shutil.ignore_patterns('data'))
            with open(f'{name}/__init__.py', 'w') as fw:
                with slinn_root('/defaults/app/__init__.py.template', 'r') as fr:
                    fw.write(pp.preprocess(fr.read(), {
                        'appname': name
                    }))
            os.makedirs(f'{apppath}/templates_data', exist_ok=True)
            try:
                shutil.copytree(f'{templates_folder}/{template_name}/data/',
                                f'{apppath}/templates_data/{template_name}')
            except (FileExistsError, FileNotFoundError):
                pass
        except (FileExistsError, FileNotFoundError):
            pass

    @staticmethod
    def delete_app(name: str, path: str = '.') -> None:
        apppath = (path + '?').replace('/?', '').replace('?', '')
        ensure_appname = replace_all(name, '-&$#!@%^().,', '_')
        if not os.path.isdir(ensure_appname):
            raise AppNotExistException(name)
        shutil.rmtree(ensure_appname)
        shutil.rmtree(f'{apppath}/templates_data/{ensure_appname}', ignore_errors=True)
        if os.path.isdir(f'{apppath}/templates_data'):
            if len(os.listdir(f'{apppath}/templates_data')) == 0:
                shutil.rmtree(f'{apppath}/templates_data')
        ProjectAPI.update_config()

    @staticmethod
    def set_project_name(name: str):
        ProjectAPI.update_config({'name': name})

    @staticmethod
    def set_host(host: str):
        ProjectAPI.update_config({'host': host})

    @staticmethod
    def set_port(port: int):
        ProjectAPI.update_config({'port': port})

    @staticmethod
    def disable_ssl():
        ProjectAPI.update_config({'ssl': {
            'fullchain': False,
            'key': False
        }})

    @staticmethod
    def set_ssl_certs(public_cert_path: str, private_cert_path: str):
        ProjectAPI.update_config({'ssl': {
            'fullchain': public_cert_path,
            'key': private_cert_path
        }})

    @staticmethod
    def set_debug(mode: bool):
        ProjectAPI.update_config({'debug': mode})

    @staticmethod
    def is_ssl() -> bool:
        config = ProjectAPI.get_config()
        return 'ssl' in config and \
            'fullchain' in config['ssl'] and \
            config['ssl']['fullchain'] and \
            'key' in config['ssl'] and \
            config['ssl']['key']

    @staticmethod
    def get_link() -> str:
        config = ProjectAPI.get_config()
        is_ssl = ProjectAPI.is_ssl()
        protocol = 'https' if is_ssl else 'http'
        return (
                f'{protocol}://' +
                (
                    '0.0.0.0' if (config['host'] is None or config['host'] == '') else (
                        '[' + config['host'] + ']' if ':' in config['host'] else config['host'])
                ) +
                f'{(":" + str(config['port']) if config['port'] != 443 else "") if is_ssl else (":" + str(config['port']) if config['port'] != 80 else "")}/'
        )

    @staticmethod
    def restart():
        args = [sys.executable] + [sys.argv[0]] + sys.argv[1:]
        os.execv(sys.executable, args)
        os._exit(0)

    @staticmethod
    def get_plugins() -> list[dict]:
        return packages()['plugins']

    @staticmethod
    def get_plugin_storage(key) -> StorageApi:
        plugin = packages()['plugins'][key]
        return StorageApi('', zip_file=f'spm_packages/Plugins/{key}.zip') if plugin['zip'] else Storage(f'spm_packages/Plugins/{key}')


if __name__ == '__main__':
    ProjectAPI.create_app('test', hosts=('well_welg.ru', 'global.marikhuana.xyz'))
    ProjectAPI.delete_app('test')
    ProjectAPI.set_project_name('Fobox Dev')
    ProjectAPI.create_app_from_template('test2', 'firstrun')
    print(ProjectAPI.get_apps())
    print(ProjectAPI.get_link())
