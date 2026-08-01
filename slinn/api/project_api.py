from slinn import root, Preprocessor
from slinn.api.storage_api import StorageApi
from slinn.tools.manage.misc import (
    replace_all, add_quotes_to_list, packages
)
from slinn.tools.manage.defaults import APP_CONFIG
from typing import Optional
import os
import tomlkit
import shutil
import sys
import slinn


slinn_root = StorageApi(root)
pp = Preprocessor()


class SlinnApiException(Exception): ...


class AppExistsException(SlinnApiException):
    def __init__(self, app_name):
        super().__init__(f'app named \'{app_name}\' exists')


class AppNotExistException(SlinnApiException):
    def __init__(self, app_name):
        super().__init__(f'app named \'{app_name}\' does not exist')


class ProjectAPI:
    @staticmethod
    def get_config() -> dict:
        with open('slinn.toml', 'rb') as project:
            project_json = tomlkit.load(project)
            if 'apps' not in project_json.keys():
                project_json['apps'] = []
            return project_json

    @staticmethod
    def update_config(updates: Optional[dict] = None) -> None:
        updates = updates or {}
        project_json = ProjectAPI.get_config()
        if 'apps' in updates:
            del updates['apps']
        project_json['apps'] = [app for app in project_json.get('apps', []) if os.path.isdir(app)]
        project_json.update(updates)
        #with open('project.json', 'w') as project:
        #    json.dump(project_json, project, indent=4)

    @staticmethod
    def create_app(name: str, hosts: tuple[str, ...] = (), *, init: bool = True) -> None:
        ensure_appname = replace_all(name, '-&$#!@%^().,', '_')
        if os.path.isdir(ensure_appname):
            raise AppExistsException(name)
        os.mkdir(ensure_appname)
        if init:
            with open(f'{ensure_appname}/__init__.py', 'w') as fw:
                with slinn_root('/defaults/app/__init__.py.template', 'r') as fr:
                    fw.write(pp.preprocess(fr.read(), {
                        'appname': ensure_appname
                    }))
            with open(f'{ensure_appname}/app.py', 'w') as fw:
                with slinn_root('/defaults/app/app.py.template', 'r') as fr:
                    fw.write(pp.preprocess(fr.read(), {
                        'hosts': ', '.join(add_quotes_to_list(hosts))
                    }))
            with open(f'{ensure_appname}/config.json', 'w') as f:
                json.dump(APP_CONFIG, f, indent=4)
        with open('project.json', 'r') as f:
            fj = json.load(f)
        if 'apps' not in fj.keys():
            fj['apps'] = []
        fj['apps'].insert(0, ensure_appname)
        with open('project.json', 'w') as f:
            json.dump(fj, f, indent=4)
        ProjectAPI.update_config()

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
    def get_apps() -> set[str]:
        return set(ProjectAPI.get_config()['apps'])

    @staticmethod
    def get_name() -> str:
        return ProjectAPI.get_config()['name']

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
    def get_plugin_storage(key) -> Storage:
        plugin = packages()['plugins'][key]
        return Storage('', zip_file=f'spm_packages/Plugins/{key}.zip') if plugin['zip'] else Storage(f'spm_packages/Plugins/{key}')


if __name__ == '__main__':
    ProjectAPI.create_app('test', hosts=('well_welg.ru', 'global.marikhuana.xyz'))
    ProjectAPI.delete_app('test')
    ProjectAPI.set_project_name('Fobox Dev')
    ProjectAPI.create_app_from_template('test2', 'firstrun')
    print(ProjectAPI.get_apps())
    print(ProjectAPI.get_link())
