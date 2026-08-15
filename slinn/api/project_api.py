from slinn import root, Preprocessor, _, Dispatcher
from slinn.tools.manage.misc import (
    replace_all, add_quotes_to_list, packages, load_module, load_imports,
    load_migrations, plugins_sorted, load_template, validate_name
)
from slinn.tools.manage.colorcodes import *
from slinn.net.address import AddressConfigFactory
from slinn.tools.manage.defaults import APP_CONFIG
from slinn.api.exceptions import (
    AppExistsException, AppNotExistException, TemplateNotExistsException, AppNameIsNotValidException
)
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
        logging.basicConfig(level=logging.WARN)
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
        if not validate_name(name):
            raise AppNameIsNotValidException(name)
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

    def delete_app(self, name: str) -> None:
        if not validate_name(name):
            raise AppNameIsNotValidException(name)
        if not os.path.isdir(name):
            raise AppNotExistException(name)

        shutil.rmtree(name)

        for i, app in enumerate(self.config.apps):
            if app.name == name:
                del self.config.apps[i]
        self.save_config()

    def install_template(self, template_name: str, app_name: str):
        if not validate_name(app_name):
            raise AppNameIsNotValidException(app_name)
        if template_name not in self.get_templates():
            raise TemplateNotExistsException(template_name)

        template = load_template(
            f'spm_packages/Templates/{template_name}/template.py',
            f'spm_packages.Templates.{template_name}'
        )
        self.create_app(app_name, init=False)
        template.install(
            os.path.abspath(app_name),
            os.path.abspath(f'spm_packages/Templates/{template_name}')
        )

    async def apply_all_migrations(self) -> int:
        plugins = self.get_plugins()

        plugins_zip = {
            key: plugin
            for key, plugin in plugins.items()
            if plugin['enabled'] and plugin['zip']
        }

        plugins_dir = {
            key: plugin
            for key, plugin in plugins.items()
            if plugin['enabled'] and not plugin['zip']
        }

        migrations = {}

        async def check_and_apply_migration(migration_meta):
            migration = migration_meta.cls()
            for dependency in migration.dependencies:
                if not migrations[dependency].applied:
                    await check_and_apply_migration(migrations[dependency])
            print(f'{GRAY}  - Checking {migration_meta.cls.__name__} from {migration_meta.display}... ', end='')
            if await migration.check():
                print(f'{GREEN}+{RESET}')
                print(f'{GRAY}  - Applying {migration_meta.cls.__name__} from {migration_meta.display}...{RESET}')
                await migration.apply()
            else:
                print(f'{RED}-{RESET}')
            if migration_meta.is_zip:
                exec(';'.join(load_imports((), (migration_meta.package_key,), (), cfg['debug'])))
            else:
                exec(';'.join(load_imports((), (), (migration_meta.package_key,), cfg['debug'])))
            migration_meta.set_applied()

        for key in plugins_zip | plugins_dir:
            is_zip = (plugins_zip | plugins_dir)[key]['zip']
            _migrations = {
                migration.cls.__name__ + f'.{key}': migration
                for migration in load_migrations(
                    os.path.join(self.path, f'spm_packages/Plugins/{key}' + ('.zip' if is_zip else '')),
                    key,
                    is_zip
                )
            }
            migrations.update(_migrations)
            for migration_meta in _migrations.values():
                if migration_meta.applied:
                    continue
                await check_and_apply_migration(migration_meta)

        migrations.update({
            migration.cls.__name__: migration
            for migration in load_migrations(
                os.path.dirname(__file__),
                self.config.project.name,
                False
            )
        })

        for migration_meta in migrations.values():
            if migration_meta.applied:
                continue
            await check_and_apply_migration(migration_meta)

        return len(migrations)

    @staticmethod
    def restart():
        args = [sys.executable] + [sys.argv[0]] + sys.argv[1:]
        os.execv(sys.executable, args)
        os._exit(0)

    @staticmethod
    def get_plugins() -> dict:
        pkgs = packages()
        return plugins_sorted(pkgs['plugins'], pkgs)

    @staticmethod
    def get_templates() -> list[dict]:
        return packages()['templates']

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
