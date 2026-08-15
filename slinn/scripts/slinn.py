from slinn.api.exceptions import (
    AppExistsException, AppNameIsNotValidException, TemplateNotExistsException, SlinnApiException
)
from slinn.tools.manage.command import Command
from slinn.tools.manage.colorcodes import *
from slinn.tools.manage.help_generator import help_generator
from slinn.tools.manage.misc import (
    add_quotes_to_list, packages, load_imports,
    load_migrations, plugins_sorted, load_template
)
from slinn import _
from slinn.api import ProjectApi, StorageApi, AppApi, ProjectConfig
from typing import Optional
import orjson
import slinn
import asyncio
import sys
import os


root_command = Command()
slinn_root = StorageApi(slinn.root)
pp = slinn.Preprocessor()


if not os.path.isfile(os.path.join(os.getcwd(), 'slinn.toml')):
    exit(f'{RED}Must be run in project`s root{RESET}')

project = ProjectApi(os.getcwd())
project.load_config()


@root_command.subcommand('run')
async def run_command():
    for message in project.run():
        yield message

@root_command.subcommand('create-app', ('name', ))
async def create_command(name: str):
    try:
        project.create_app(name)
    except SlinnApiException as e:
        return str(e).capitalize(), RED
    return _('App successfully created'), GREEN

@root_command.subcommand('delete-app', ('name',))
async def delete_command(name):
    if input(_('Are you sure? (y/N) >>> ')).lower() not in ('y', 'yes', _('y'), _('yes')):
        return _('Aborted')
    try:
        project.delete_app(name)
    except SlinnApiException as e:
        return str(e).capitalize(), RED
    return _('App successfully deleted'), GREEN

@root_command.subcommand('template', ('template_name', 'app_name'))
async def template_command(template_name, app_name):
    try:
        project.install_template(template_name, app_name)
    except SlinnApiException as e:
        return str(e).capitalize(), RED
    return _('Template \'{template_name}\' successfully installed as \'{app_name}\'').format(
        template_name = template_name, app_name = app_name), GREEN

@root_command.subcommand('migrate-all')
async def apply_all_migrations():
    try:
        return _('Found {migrations_count} migrations total').format(
            migrations_count = await project.apply_all_migrations()
        ), GREEN
    except SlinnApiException as e:
        return str(e).capitalize(), RED


@root_command.subcommand('help')
async def help_command():
    return help_generator('Slinn Manager', sys.argv[0], {
        'run': 'start server',
        'create-app {app`s name} host=(host1) host=(host2)...': 'create a new app',
        'delete-app {app`s name} (project`s path)': 'delete an app',
        'template {template`s name} (projects`s path)': 'install a template app',
        'migrate-all': 'apply migrations',
        'help': 'display this message',
        'version': 'display slinn`s version'
    })

@root_command.subcommand('version')
async def version_command():
    return slinn.version

@root_command.command_not_exists()
async def command_not_exists():
    yield f'Command {sys.argv[1].lower()} is not exists', RED

@root_command.command_not_specified()
async def command_not_specified():
    yield f'{RED}Command was not specified{RESET}'


def main():
    try:
        asyncio.run(root_command(sys.argv[1:]))
    except KeyboardInterrupt:
        print(f'\n\n{BLUE}{BOLD}KeyboardInterrupt{RESET}')

if __name__ == '__main__':
    main()
