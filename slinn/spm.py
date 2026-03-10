from slinn import slinn_root, Storage
from .tools.manage.command import Command
from .tools.manage.colorcodes import *
import sys
import os
import json
import urllib.request
import urllib.error
import urllib.parse
import email
import zipfile


version = 'Slinn Package Manager 26.3a'
root_command = Command()

spm_config = {
    'mirrors': {
        'miot': [
            'https://miot.su/repos'
        ]
    },
    'repositories': {
        'fobox.core': {
            'name': 'Fobox Core',
            'type': 'http',
            'server': 'miot'
        }
    }
}

slinn_root.makedirs('spm/repositories')
slinn_root.makedirs('spm/tmp')
if slinn_root.isfile('spm/spm.json'):
    with slinn_root('spm/spm.json', 'r') as f:
        spm_config.update(json.load(f))
with slinn_root('spm/spm.json', 'w') as f:
    json.dump(spm_config, f, ensure_ascii=False, indent=4)


@root_command.command_not_specified()
@root_command.subcommand('help')
def no_args_handler():
    commands_desc = {
        'update': 'update packages metadata from repositories',
        'install': 'install or upgrade package',
        #'uninstall': 'uninstall package',
        #'info': 'display package information',
        #'search': 'search for packages',
        #'list': 'display all installed packages',
        'list-repos': 'display all repositories',
        'list-packages': 'display all packages in repositories',
        'help': 'display this message',
        'version': 'display version'
    }
    print((f'{BOLD}{version}{RESET}\n\n'
          f'{CYAN}Usage{RESET}:\n'
          f'  {sys.argv[0]} <command>\n\n'
          f'{CYAN}Commands{RESET}:\n') + '\n'.join(
        [f'  {BOLD}{name:20}{RESET}{desc.capitalize()}.' for name, desc in commands_desc.items()]
    ))


@root_command.subcommand('update')
def update():
    for i, (key, repo) in enumerate(spm_config['repositories'].items()):
        if repo['type'] == 'http':
            updated = False
            print(f'Updating {BOLD}{repo["name"]}{RESET} repository...')
            for mirror in spm_config['mirrors'][repo['server']]:
                try:
                    with urllib.request.urlopen(mirror+'/'+key, timeout=5) as resp:
                        repo_data = json.load(resp)
                        with slinn_root(f'spm/repositories/{key}.json', 'w') as f:
                            f.write(json.dumps(repo_data, ensure_ascii=False, indent=4))
                    updated = True
                    break
                except urllib.error.HTTPError as e:
                    print(f'  - {YELLOW}Failed to update {BOLD}{repo["name"]}{RESET} {GRAY}({e.code} {e.reason} at {mirror+"/"+key}){RESET}')
                    continue
                except urllib.error.URLError as e:
                    print(f'  - {YELLOW}Failed to update {BOLD}{repo["name"]}{RESET} {GRAY}({e.reason} at {mirror + "/" + key}){RESET}')
                    continue
                except json.decoder.JSONDecodeError as e:
                    print(f'  - {YELLOW}Failed to update {BOLD}{repo["name"]}{RESET} {GRAY}(JSONDecodeError at {mirror + "/" + key}){RESET}')
                    continue
            if not updated:
                print(f'{RED}Failed to update {BOLD}{repo["name"]}{RESET}{RED} due to not a single mirror responded correctly{RESET}')
            else:
                print(f'{GREEN}{BOLD}{repo["name"]}{RESET}{GREEN} has updated successfully{RESET}')
        else:
            print(f'{GRAY}Skip {repo["type"]} repository {BOLD}{repo["name"]}{RESET}')


@root_command.subcommand('install')
def install(args):
    if not os.path.isfile(os.getcwd()+'/project.json'):
        print(f'{RED}Not in Slinn project directory.{RESET}')
        return
    project = Storage(os.getcwd())
    if len(args['not_used']) == 0:
        print(f'{GRAY}Nothing to do{RESET}')
        return
    to_install = []
    for keys in args['not_used']:
        keys = keys.split('@')
        if len(keys) > 2:
            print(f'{RED}Package name is invalid.{RESET}')
            return
        pack_key = keys[0]
        repo_key = keys[1] if len(keys) == 2 else None
        package = None
        if not repo_key:
            print(f'{YELLOW}Repository for {BOLD}{pack_key}{RESET}{YELLOW} is not specified. Searching in all repositories...{RESET}')
            for key, repo in spm_config['repositories'].items():
                if not slinn_root.isfile(f'spm/repositories/{key}.json'):
                    print(f'{YELLOW}Repository {BOLD}{repo["name"]}{RESET}{YELLOW} `s file not found. {GRAY}(had you forgotten to update?){RESET}')
                    continue
                with slinn_root(f'spm/repositories/{key}.json', 'r') as f:
                    packages = json.load(f)['packages']
                    if pack_key in packages.keys():
                        package = packages[pack_key]
                        repo_key = key
                        break
            if not package:
                print(f'{RED}{BOLD}{pack_key}{RESET}{RED} not found.{RESET}')
                return
            print(f'{GRAY}Found {pack_key}@{repo_key}.{RESET}')
        else:
            if repo_key not in spm_config['repositories']:
                print(f'{RED}Repository {BOLD}{repo_key}{RESET}{RED} not found.{RESET}')
                return
            repo = spm_config['repositories'][repo_key]
            if not slinn_root.isfile(f'spm/repositories/{repo_key}.json'):
                print(f'{YELLOW}Repository {BOLD}{repo["name"]}{RESET}{YELLOW} `s file not found. {GRAY}(had you forgotten to update?){RESET}')
                return
            with slinn_root(f'spm/repositories/{repo_key}.json', 'r') as f:
                packages = json.load(f)['packages']
                if pack_key in packages.keys():
                    package = packages[pack_key]
                else:
                    print(f'{RED}{BOLD}{pack_key}@{repo_key}{RESET}{RED} not found.{RESET}')
                    return
        ver = f'v{package["version"]["major"]}.{package["version"]["minor"]}.{package["version"]["patch"]}'
        print(f'Requesting {pack_key}@{repo_key}{GRAY}[{ver}]{RESET}...')
        try:
            with urllib.request.urlopen(package['url']) as response:
                size_bytes = int(response.headers.get('Content-Length'))
                content_disposition = response.headers.get('Content-Disposition')
                if content_disposition:
                    msg = email.message.EmailMessage()
                    msg['Content-Disposition'] = content_disposition
                    filename = msg.get_filename()
                if not filename:
                    filename = os.path.basename(urllib.parse.urlparse(response.geturl()).path)
                to_install.append({
                    'pack_key': pack_key,
                    'repo_key': repo_key,
                    'package': package,
                    'size_bytes': size_bytes,
                    'filename': filename,
                    'path': os.path.join(slinn_root.get_path('spm/tmp/'), filename),
                    'ver': ver
                })
        except urllib.error.HTTPError as e:
            print(f'{RED}Failed to request {pack_key}@{repo_key}[{ver}] {GRAY}({e.code} {e.reason}){RED}.{RESET}')
            return
        except urllib.error.URLError as e:
            print(f'{RED}Failed to request {pack_key}@{repo_key}[{ver}] {GRAY}({e.reason}){RED}.{RESET}')
            return

    print(
        'Are you sure to install ' +
        ', '.join([
            f'{v["pack_key"]}@{v["repo_key"]}{GRAY}'
            f'[{v["ver"]}]{RESET}'
            for v in to_install
        ]) + ' (' + str(round(sum(map(lambda v: v["size_bytes"] or 0, to_install)) / 1024 ** 2, 2)) + 'MiB total) [Y/n] > ',
        end=''
    )

    if input().lower().strip() not in ('', 'y', 'yes'):
        print(f'{GRAY}Aborted by user{RESET}')
        return

    project.makedirs('spm_packages/Plugins')
    packages = {
        'plugins': {},
        'templates': {},
        'apps': {}
    }
    if project.isfile('spm_packages/packages.json'):
        with project('spm_packages/packages.json', 'r') as f:
            packages = json.load(f)
    for v in to_install:
        try:
            urllib.request.urlretrieve(v['package']['url'], v['path'])
            print(f'  - Downloaded {v["pack_key"]}@{v["repo_key"]}{GRAY}[{v["ver"]}]{RESET}.')
            manifest = {}
            with zipfile.ZipFile(v['path']) as zf:
                if 'manifest.json' not in zf.namelist():
                    print(f'  - {RED}{v["pack_key"]}@{v["repo_key"]}[{v["ver"]}] manifest file not found.{RESET}')
                    return
                manifest = json.load(zf.open('manifest.json'))
                if manifest.get('manifestVersion', 1) not in (1, ):
                    print(f'  - {RED}{v["pack_key"]}@{v["repo_key"]}[{v["ver"]}] manifest version {manifest.get("manifestVersion", 1)} is not supported.{RESET}')
                    return
            if manifest['type'] == 'plugin':
                packages['plugins'][v['pack_key']] = {
                    'displayName': manifest.get('displayName', v['pack_key']),
                    'description': manifest.get('description', v['package']['description']),
                    'version': manifest.get('version', v['package']['version']),
                    'contributors': manifest.get('contributors', []),
                    'links': manifest.get('links', []),
                    'enabled': True,
                    'zip': manifest.get('zipSafe', False),
                    'includes': [],
                    'dependencies': manifest.get('dependencies', []),
                    'plugin': manifest.get('plugin', {
                        'dispatchers': []
                    })
                }
                if manifest.get('zipSafe', True):
                    packages['plugins'][v['pack_key']]['includes'].append(f'spm_packages/Plugins/{v["pack_key"]}.zip')
                    if not project.isfile(f'spm_packages/Plugins/{v["pack_key"]}.zip'):
                        os.rename(v['path'], project.get_path(f'spm_packages/Plugins/{v["pack_key"]}.zip'))
                        print(f'  - Installed {v["pack_key"]}@{v["repo_key"]}{GRAY}[{v["ver"]}]{RESET}.')
                    else:
                        project.remove(f'spm_packages/Plugins/{v["pack_key"]}.zip')
                        os.rename(v['path'], project.get_path(f'spm_packages/Plugins/{v["pack_key"]}.zip'))
                        print(f'  - Reinstalled {v["pack_key"]}@{v["repo_key"]}{GRAY}[{v["ver"]}]{RESET}.')
                else:
                    packages['plugins'][v['pack_key']]['includes'].append(f'spm_packages/Plugins/{v["pack_key"]}')
                    if not project.isdir(f'spm_packages/Plugins/{v["pack_key"]}'):
                        with zipfile.ZipFile(v['path']) as zf:
                            zf.extractall(project.get_path(f'spm_packages/Plugins/{v["pack_key"]}'))
                        print(f'  - Installed {v["pack_key"]}@{v["repo_key"]}{GRAY}[{v["ver"]}]{RESET}.')
                    else:
                        project.rmtree(f'spm_packages/Plugins/{v["pack_key"]}')
                        with zipfile.ZipFile(v['path']) as zf:
                            zf.extractall(project.get_path(f'spm_packages/Plugins/{v["pack_key"]}'))
                        print(f'  - Reinstalled {v["pack_key"]}@{v["repo_key"]}{GRAY}[{v["ver"]}]{RESET}.')
            else:
                print(f'  - {RED}{v["pack_key"]}@{v["repo_key"]}[{v["ver"]}] package type {manifest["type"]} is not supported.{RESET}')
                return
            with project('spm_packages/packages.json', 'w') as f:
                f.write(json.dumps(packages, ensure_ascii=False, indent=4))
        except urllib.error.HTTPError as e:
            print(f'{RED}Failed to request {v["pack_key"]}@{v["repo_key"]}[{v["ver"]}] {GRAY}({e.code} {e.reason}){RED}.{RESET}')
            return
        except urllib.error.URLError as e:
            print(f'{RED}Failed to request {v["pack_key"]}@{v["repo_key"]}[{v["ver"]}] {GRAY}({e.reason}){RED}.{RESET}')
            return


@root_command.subcommand('list-repos')
def list_repos():
    for i, (key, repo) in enumerate(spm_config['repositories'].items()):
        if repo['type'] == 'http':
            print(f'{str(i+1)+". ":<4}HTTP {BOLD}{repo["name"]}{RESET} repository ({key}) at {repo["baseUrl"]}')
        else:
            print(f'{str(i + 1) + ". ":<4}Unsupported {repo["type"]} repository {BOLD}{repo["name"]}{RESET} ({key})')
    print(f'\nTotal {len(spm_config["repositories"])} repositories')


@root_command.subcommand('list-packages')
def list_packages():
    count = 0
    for repo_key, repo in spm_config['repositories'].items():
        if not slinn_root.isfile(f'spm/repositories/{repo_key}.json'):
            print(f'{YELLOW}Repository {BOLD}{repo["name"]}{RESET}{YELLOW} `s file has not found. {GRAY}(had you forgotten to update?){RESET}')
            continue
        print(f'{BOLD}{repo["name"]}{RESET} packages:')
        with slinn_root(f'spm/repositories/{repo_key}.json', 'r') as f:
            for i, (key, package) in enumerate(json.load(f)['packages'].items()):
                ver = f'v{package["version"]["major"]}.{package["version"]["minor"]}.{package["version"]["patch"]}'
                print(f'{str(i + 1) + ". ":<5}{BOLD}{key}@{repo_key}{RESET}{GRAY}[{ver}]{RESET} - {package["description"]}')
                count += 1
    print(f'\nTotal {count} available packages')


@root_command.subcommand('version')
def display_version():
    print(version)



def main():
    root_command(sys.argv[1:])()

if __name__ == '__main__':
    main()
