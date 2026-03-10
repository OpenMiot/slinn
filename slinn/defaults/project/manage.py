from slinn.tools.manage.colorcodes import *
from slinn.tools.manage.misc import (
    replace_all, add_quotes_to_list, config, packages, get_dispatchers, app_config, load_imports, app_reload,
    load_migrations, load_migrations_from_zip, plugins_sorted, load_template
)
from slinn.tools.manage.command import Command
from slinn.tools.manage.defaults import APP_CONFIG
from slinn.preprocessor import Preprocessor
from slinn import slinn_root, ProjectAPI
import sys
import os
import shutil
import json
import slinn
import asyncio
import inspect
import warnings


root_command = Command()
pp = Preprocessor()
cfg = config()
pkgs = packages()
pkgs['plugins'] = plugins_sorted(pkgs['plugins'], pkgs)

plugins_zip = {
    key: plugin
    for key, plugin in pkgs['plugins'].items()
    if plugin['enabled'] and plugin['zip']
}

plugins_dir = {
    key: plugin
    for key, plugin in pkgs['plugins'].items()
    if plugin['enabled'] and not plugin['zip']
}


@root_command.subcommand('run')
def run_command():
    apps_info = []
    for app in cfg['apps']:
        if not app_config(app)['debug'] or cfg['debug']:
            apps_info.append(app)
        else:
            apps_info.append('[' + STRIKE + app + NONSTRIKE + ']')

    plugins_info = []
    for plugin in pkgs['plugins'].values():
        if plugin['enabled']:
            plugins_info.append(plugin['displayName'])
        else:
            plugins_info.append('[' + STRIKE + plugin['displayName'] + NONSTRIKE + ']')

    dps = get_dispatchers(cfg['apps'], plugins_zip, plugins_dir, cfg["debug"])
    if not dps:
        return print(f'{RED}Dispatchers not found. Check your apps, packages and ./project.json{RESET}')

    print(GRAY, end='')
    if apps_info:
        print('Apps: ' + ', '.join(apps_info))
    if plugins_info:
        print('Plugins: ' + ', '.join(plugins_info))
    print('Debug mode ' + ('enabled' if cfg['debug'] else 'disabled'))
    print('Smart navigation ' + ('enabled' if cfg['smart_navigation'] else 'disabled'))
    print(RESET)
    print('Starting server...')
    print(f'{BOLD}Press CTRL+C to quit{RESET}')
    with slinn_root('/tools/manage/runner.py.template', 'r') as f:
        cfg['smart_navigation'] = str(cfg['smart_navigation'])
        if 'fullchain' in cfg['ssl'].keys() and 'key' in cfg['ssl'].keys():
            cfg['ssl_fullchain'] = '"' + cfg['ssl']['fullchain'] + '"' if cfg['ssl']['fullchain'] else 'None'
            cfg['ssl_key'] = '"' + cfg['ssl']['key'] + '"' if cfg['ssl']['key'] else 'None'
        return exec(pp.preprocess(f.read(), {
            'imports': ';'.join(load_imports(cfg['apps'], plugins_zip, plugins_dir, cfg['debug'])),
            'reloads': ''.join([app_reload(app) for app in cfg['apps'] if not app_config(app)['debug'] or cfg['debug']]),
            'server_reload': ','.join([f'{app}.dp' for app in cfg['apps'] if not app_config(app)['debug'] or cfg['debug']]),
            'dps': dps,
            **cfg
        }))


@root_command.subcommand('create', ('name', 'host'))
def create_command(args):
    if 'name' not in args.keys():
        return print(f'{RED}The app`s name is not specified{RESET}')
    ensure_appname = replace_all(args['name'], '-&$#!@%^().,', '_')
    if os.path.isdir(ensure_appname):
        return print(f'{BLUE}The app named {args["name"]} exists{RESET}')
    if 'host' not in args.keys():
        print(f'{BLUE}Hosts were not specified')
    os.mkdir(ensure_appname)
    with open(f'{ensure_appname}/__init__.py', 'w') as fw:
        with slinn_root('/defaults/app/__init__.py.template', 'r') as fr:
            fw.write(pp.preprocess(fr.read(), {
                'appname': ensure_appname
            }))
    with open(f'{ensure_appname}/app.py', 'w') as fw:
        with slinn_root('/defaults/app/app.py.template', 'r') as fr:
            fw.write(pp.preprocess(fr.read(), {
                'hosts': (
                    ''
                    if 'host' not in args.keys() else
                    ', '.join(
                        add_quotes_to_list(
                            args['host']
                            if type(args['host']) is list else
                            [args['host']]
                        )
                    )
                )
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
    update()
    return print(f'{GREEN}App successfully created{RESET}')


@root_command.subcommand('delete', ('name',))
def delete_command(args):
    apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
    if 'name' not in args.keys():
        return print(f'{RED}The app`s name is not specified{RESET}')
    ensure_appname = replace_all(args['name'], '-&$#!@%^().,', '_')
    if not os.path.isdir(ensure_appname):
        return print(f'{BLUE}The app named {args["name"]} does not exist{RESET}')
    if input(f'{RESET}Are you sure? (y/N) >>> ').lower() not in ['y', 'yes']:
        return print(f'{RESET}Aborted')
    shutil.rmtree(ensure_appname)
    shutil.rmtree(f'{apppath}/templates_data/{ensure_appname}', ignore_errors=True)
    if os.path.isdir(f'{apppath}/templates_data') and len(os.listdir(f'{apppath}/templates_data')) == 0:
        shutil.rmtree(f'{apppath}/templates_data')
    update()
    return print(f'{GREEN}App successfully deleted{RESET}')


@root_command.subcommand('update')
def update():
    with open('project.json', 'r') as project:
        project_json = json.load(project)
    if 'apps' not in project_json.keys():
        return print(f'Updated project.json')
    project_json['apps'] = [app for app in project_json['apps'] if os.path.isdir(app)]
    with open('project.json', 'w') as project:
        json.dump(project_json, project, indent=4)
    return print(f'Updated project.json')


@root_command.subcommand('help')
def help_command():
    with slinn_root('/tools/manage/manager_help.template', 'r') as f:
        print(pp.preprocess(f.read(), {
            'cmd': f'py {sys.argv[0]}',
            'gray': GRAY,
            'reset': RESET,
            'bold': BOLD
        }))


@root_command.subcommand('version')
def version_command():
    print(slinn.version)


@root_command.subcommand('_template', ('name', 'path'))
def template_command(args):
    apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
    if 'name' not in args.keys():
        return print(f'{RED}Template name not specified{RESET}')
    with open('project.json', 'r') as f:
        fj = json.load(f)
    if 'apps' not in fj.keys():
        fj['apps'] = []
    if args['name'] in fj['apps']:
        return print(f'{BLUE}Template {args["name"]} has already installed{RESET}')
    fj['apps'].insert(0, args['name'])
    with open('project.json', 'w') as f:
        json.dump(fj, f, indent=4)
    try:
        shutil.copytree(f'{slinn.root}/templates/{args["name"]}/', f'{apppath}/{args["name"]}',
                        ignore=shutil.ignore_patterns('data'))
        os.makedirs(f'{apppath}/templates_data', exist_ok=True)
        try:
            shutil.copytree(f'{slinn.root}/templates/{args["name"]}/data/',
                            f'{apppath}/templates_data/{args["name"]}')
        except (FileExistsError, FileNotFoundError):
            pass
        update()
        print(f'{GREEN}Template {args["name"]} successfully installed{RESET}')
    except FileExistsError:
        print(f'{BLUE}Template {args["name"]} has already installed{RESET}')
    except FileNotFoundError:
        print(f'{BLUE}Template {args["name"]} not found{RESET}')


@root_command.subcommand('template', ('template', 'app_name'))
def _template_command(args):
    if not {'template', 'app_name'}.issubset(args.keys()):
        print(f'{RED}Package or app`s name not specified{RESET}')
        return
    app_name = replace_all(args['app_name'], '-&$#!@%^().,', '_')
    if '/' in app_name:
        print(f'{RED}App`s name invalid{RESET}')
        return
    if args['template'] not in pkgs['templates']:
        print(f'{RED}Template not found{RESET}')
        return
    template = load_template(
        f'spm_packages/Templates/{args["template"]}/template.py',
        f'spm_packages.Templates.{args["template"]}'
    )
    try:
        ProjectAPI.create_app(app_name, init=False)
    except slinn.project_api.AppExistsException:
        print(f'{BLUE}The app named {args["app_name"]} exists{RESET}')
        return
    template.install(
        os.path.abspath(app_name),
        os.path.abspath(f'spm_packages/Templates/{args["template"]}')
    )
    print(f'{GREEN}Template {args["template"]} successfully installed as {app_name}{RESET}')



@root_command.subcommand('migrate_app', ('name',))
def migrate_app_command(args):
    if 'name' not in args.keys():
        return print(f'{RED}The app`s name is not specified{RESET}')
    ensure_appname = replace_all(args['name'], '-&$#!@%^().,', '_')
    if not os.path.isdir(ensure_appname):
        return print(f'{BLUE}The app named {args["name"]} does not exist{RESET}')
    with open(f'{ensure_appname}/__init__.py', 'w') as fw:
        with slinn_root('/defaults/app/__init__.py.template', 'r') as fr:
            fw.write(pp.preprocess(fr.read(), {
                'appname': ensure_appname
            }))
    with open(f'{ensure_appname}/config.json', 'w') as f:
        json.dump(APP_CONFIG, f, indent=4)
    return print(f'{GREEN}App successfully migrated{RESET}')


@root_command.subcommand('makemigrations')
def apply_all_migrations(args):
    warnings.filterwarnings("ignore", category=DeprecationWarning)  # TODO: fix warnings

    migrations = {
        migration.cls.__name__: migration
        for migration in load_migrations(
            os.path.join(os.path.dirname(__file__), f'migrations/*.py'),
            'migrations'
        )
    }

    exec(';'.join(load_imports(cfg['apps'], plugins_zip, plugins_dir, cfg['debug'])))

    for key in plugins_zip:
        migrations.update({
            migration.cls.__name__ + f'.{key}': migration
            for migration in load_migrations_from_zip(
                os.path.join(os.path.dirname(__file__), f'spm_packages/Plugins/{key}.zip'),
                f'spm_packages.Plugins.{key}.migrations'
            )
        })

    for key in plugins_dir:
        migrations.update({
            migration.cls.__name__ + f'.{key}': migration
            for migration in load_migrations(
                os.path.join(os.path.dirname(__file__), f'spm_packages/Plugins/{key}/migrations/*.py'),
                f'spm_packages.Plugins.{key}.migrations'
            )
        })

    print(f'{BLUE}Found {len(migrations)} migrations{RESET}')

    async def check_and_apply_migration(migration_meta):
        migration = migration_meta.cls()
        for dependency in migration.dependencies:
            if not migrations[dependency].applied:
                await check_and_apply_migration(migrations[dependency])
        print(f'{GRAY}  - Checking {migration_meta.cls.__name__} from migrations/{migration_meta.basename}... ', end='')
        if await migration.check():
            print(f'{GREEN}+{RESET}')
            print(
                f'{GRAY}  - Applying {migration_meta.cls.__name__} from migrations/{migration_meta.basename}...{RESET}')
            await migration.apply()
        else:
            print(f'{RED}-{RESET}')
        migration_meta.set_applied()

    for migration_meta in migrations.values():
        if migration_meta.applied:
            continue
        asyncio.run(check_and_apply_migration(migration_meta))

    warnings.filterwarnings("default", category=DeprecationWarning)


@root_command.command_not_exists()
def command_not_exists():
    print(f'{RED}Command {sys.argv[1].lower()} is not exists{RESET}')


@root_command.command_not_specified()
def command_not_specified():
    print(f'{RED}Command was not specified{RESET}')


if __name__ == '__main__':
    try:
        root_command(sys.argv[1:])()
    except KeyboardInterrupt:
        print(f'\n\n{BLUE}{BOLD}KeyboardInterrupt{RESET}')
