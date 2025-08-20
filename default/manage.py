from __future__ import annotations
import sys
import os
import shutil
import json
import base64
import slinn


RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'
RESET = '\u001b[0m'
BOLD = '\u001b[1m'
GRAY = '\u001b[38;2;127;127;127m'


def arg_parse(arg: str):
    return base64.urlsafe_b64decode(arg.removeprefix('b64@').encode() + b'==').decode() if arg.startswith(
        'b64@') else arg


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
    Ds = ['\n', ' ']
    Qs = ['"', "'", '`']
    spls = splits(text, Ds, Qs)
    i = 0
    while i < len(spls):
        arg = str(spls[i])
        try:
            if arg.strip().endswith('='):
                W = arg.strip().removesuffix('=').strip()
                expecting.pop(expecting.index(W))
                args[W] = arg_parse(str(splits[i + 1]))
                i += 2
                continue
            if len(splits(arg, ['='], Qs)) == 2:
                spl = splits(arg, ['='])
                W = str(spl[0])
                if W not in args.keys():
                    args[W] = arg_parse(str(spl[1]))
                    expecting.pop(expecting.index(W))
                else:
                    args[W] = [args[W]]
                    args[W].append(arg_parse(str(spl[1])))
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


def add_quotes_to_list(lst: list[str]):
    for l in lst:
        yield f'\'{l}\''


def update():
    project = open('project.json', 'r')
    project_json = json.loads(project.read())
    project.close()
    if 'apps' not in project_json.keys():
        return print(f'Updated project.json')
    apps = []
    for app in project_json['apps']:
        if os.path.isdir(app):
            apps.append(app)
    project_json['apps'] = apps
    project = open('project.json', 'w')
    project.write(json.dumps(project_json, indent=4))
    project.close()
    return print(f'Updated project.json')


def main():
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'run':
            from slinn import Server, Address

            def config(default=None):
                cfg = default or {}
                file = open('project.json')
                cfg.update(json.loads(file.read()))
                file.close()
                return cfg

            def app_config(app):
                try:
                    cfg = {"debug": False}
                    file = open(f'{app}/config.json')
                    cfg.update(json.loads(file.read()))
                    file.close()
                    return cfg
                except FileNotFoundError:
                    print(f'{RED}{app}/config.json file not found{RESET}')
                    exit()

            def load_imports(apps, debug=False):
                imports = []
                for app in apps:
                    if not app_config(app)['debug'] or debug:
                        imports.append(f'import {app}')
                return imports

            def get_dispatchers(apps, debug=False):
                dispachers = []
                for app in apps:
                    if not app_config(app)['debug'] or debug:
                        dispachers.append(f'{app}.dp')
                return dispachers

            def app_reload(app):
                return f'global {app};{app} = importlib.reload({app});'

            print('Loading config...')
            cfg = config(default={
                'name': 'slinn',
                'debug': False,
                'apps': [],
                'port': 8080,
                'host': 'localhost',
                'timeout': 0.03,
                'max_bytes_per_receive': 4096,
                'max_bytes': 4294967296,
                'smart_navigation': True,
                'ssl': {
                    'fullchain': None,
                    'key': None
                }
            })
            name = cfg["name"]
            debug = cfg["debug"]
            apps = cfg['apps']
            port = cfg['port']
            host = cfg['host']
            timeout = float(cfg['timeout'])
            max_bytes_per_receive = int(cfg['max_bytes_per_receive'])
            max_bytes = int(cfg['max_bytes'])
            smart_navigation = cfg['smart_navigation']
            ssl_fullchain, ssl_key = None, None
            if 'fullchain' in cfg['ssl'].keys() and 'key' in cfg['ssl'].keys():
                ssl_fullchain = '"' + cfg['ssl']['fullchain'] + '"' if cfg['ssl']['fullchain'] else None
                ssl_key = '"' + cfg['ssl']['key'] + '"' if cfg['ssl']['key'] else None
            dps = get_dispatchers(apps, debug)
            if not dps:
                print(f'{RED}Dispatchers not found. Check your apps and ./project.json{RESET}')
                exit()
            global get_dir_checksum

            def get_dir_checksum(dir):
                import hashlib
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

            global checksum
            checksum = get_dir_checksum('.')

            reloader = """
def reloader(server):
	import importlib, traceback
	global checksum
	try:
		if checksum != get_dir_checksum('.'):
			checksum = get_dir_checksum('.')
			"""
            for app in cfg['apps']:
                if not app_config(app)['debug'] or debug:
                    reloader += app_reload(app)
            reloader += """
			server.reload("""
            reloader += ",".join(dps)
            reloader += """)
	except Exception:
		print('During handling request, an exception has occured:')
		traceback.print_exc()
"""

            apps_info = []
            for app in cfg['apps']:
                if not app_config(app)['debug'] or debug:
                    apps_info.append(app)
                else:
                    apps_info.append('[' + app + ']')
            print(f'{GRAY}Apps: ' + ', '.join(apps_info))
            print('Debug mode ' + 'enabled' if debug else 'disabled')
            print('Smart navigation ' + ('enabled' if smart_navigation else 'disabled'))
            print(RESET)

            import logging
            logging.basicConfig(filename=f'{name}.journal.log', level=logging.INFO)

            print('Starting server...')
            start = ';'.join(load_imports(apps, debug)) + reloader + '\n'.join([line.strip() for line in f"""
			from htrf import htrf
			server=Server(
				{",".join(dps)}, 
				smart_navigation = {smart_navigation},
				ssl_fullchain = {ssl_fullchain},
				ssl_key = {ssl_key},
				timeout = {timeout},
				max_bytes_per_receive = {max_bytes_per_receive},
				max_bytes = {max_bytes}, _func=reloader,
				htrf = htrf)
			server.listen(Address({port}, "{host}"))
			""".split('\n')])
            exec(start)
        elif sys.argv[1].lower() == 'create':
            args = get_args(['name', 'host'], ' '.join(sys.argv[2:]))
            if 'name' not in args.keys():
                return print(f'{RED}The app`s name is not specified{RESET}')
            ensure_appname = replace_all(args['name'], '-&$#!@%^().,', '_')
            if os.path.isdir(ensure_appname):
                return print(f'{BLUE}The app named {args["name"]} exists{RESET}')
            if 'host' not in args.keys():
                print(f'{BLUE}Hosts were not specified')
            os.mkdir(ensure_appname)
            with open(f'{ensure_appname}/__init__.py', 'w') as f:
                data = """import sys, importlib
if '%appname%.app' not in sys.modules.keys():
    from %appname%.app import dp
else:
    dp = importlib.reload(sys.modules['%appname%.app']).dp
""".replace('%appname%', ensure_appname)
                f.write(data)
            with open(f'{ensure_appname}/app.py', 'w') as f:
                data = """from slinn import Dispatcher, LinkFilter, AnyFilter, Response, Render

dp = Dispatcher(%hosts%)

# Write your code down here                         
""".replace('%appname%', ensure_appname).replace('%hosts%', '' if 'host' not in args.keys() else ', '.join(
                    add_quotes_to_list(args['host'] if type(args['host']) == list else [args['host']])))
                f.write(data)
            with open(f'{ensure_appname}/config.json', 'w') as f:
                data = """
{
	"debug": false
}
"""
                f.write(data)
            fr = open('project.json', 'r')
            fj = json.loads(fr.read())
            fr.close()
            if 'apps' in fj.keys():
                fj['apps'].insert(0, ensure_appname)
            else:
                fj['apps'] = []
            fw = open('project.json', 'w')
            fw.write(json.dumps(fj, indent=4))
            fw.close()
            update()
            print(f'{GREEN}App successfully created{RESET}')
        elif sys.argv[1].lower() == 'delete':
            args = get_args(['name'], ' '.join(sys.argv[2:]))
            apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
            if 'name' not in args.keys():
                return print(f'{RED}The app`s name is not specified{RESET}')
            ensure_appname = replace_all(args['name'], '-&$#!@%^().,', '_')
            if not os.path.isdir(ensure_appname):
                return print(f'{BLUE}The app named {args["name"]} does not exist{RESET}')
            if input(f'{RESET}Are you sure? (y/N) >>> ').lower() not in ['y', 'yes']:
                return print(f'{RESET}Aborted')
            shutil.rmtree(ensure_appname)
            if os.path.isdir(f'{apppath}/templates_data/{ensure_appname}'):
                shutil.rmtree(f'{apppath}/templates_data/{ensure_appname}')
            if len(os.listdir(f'{apppath}/templates_data')) == 0:
                shutil.rmtree(f'{apppath}/templates_data')
            update()
            return print(f'{GREEN}App successfully deleted{RESET}')
        elif sys.argv[1].lower() == 'update':
            return update()
        elif sys.argv[1].lower() == 'help':
            return print("""%BOLD%Slinn manager help page

Commands%RESET%:
	%cmd% run                                                              %GRAY%# Starts server%RESET%
	%cmd% create {app`s name} host=(host1) host=(host2)...                 %GRAY%# Creates a new app
		Example: %cmd% create localhost host=localhost host=127.0.0.1%RESET%
	%cmd% delete {app`s name} (project`s path)                             %GRAY%# Deletes an app
		Example: %cmd% delete localhost%RESET%
	%cmd% template {template`s name} (projects`s path)                     %GRAY%# Installs a template
		Example: %cmd% template firstrun%RESET%
	%cmd% update                                                           %GRAY%# Updates project.py%RESET%
	%cmd% migrate_app {app`s name}                                         %GRAY%# Migrates app(check slinn.guides.migration1xx2xx.migration1xx2xx)%RESET%
	%cmd% help                                                             %GRAY%# Prints this help%RESET%
	%cmd% version                                                          %GRAY%# Prints version of Slinn%RESET%
""".replace('%cmd%', f'py {sys.argv[0]}').replace('%GRAY%', GRAY).replace('%RESET%', RESET).replace('%BOLD%', BOLD))
        elif sys.argv[1].lower() == 'version':
            return print(slinn.version)
        elif sys.argv[1].lower() == 'template':
            args = get_args(['name', 'path'], ' '.join(sys.argv[2:]))
            apppath = (args['path'] + '?').replace('/?', '').replace('?', '') if 'path' in args.keys() else '.'
            if 'name' not in args.keys():
                return print(f'{RED}Template name is not specified{RESET}')
            modulepath = os.path.abspath(slinn.__file__).replace('__init__.py', '')
            fr = open('project.json', 'r')
            fj = json.loads(fr.read())
            fr.close()
            if 'apps' in fj.keys():
                if args['name'] in fj['apps']:
                    return print(f'{BLUE}Template {args["name"]} has already installed{RESET}')
                fj['apps'].insert(0, args['name'])
            else:
                fj['apps'] = []
            fw = open('project.json', 'w')
            fw.write(json.dumps(fj, indent=4))
            fw.close()
            try:
                shutil.copytree(f'{modulepath}templates/{args["name"]}/', f'{apppath}/{args["name"]}',
                                ignore=shutil.ignore_patterns('data'))
                try:
                    if not os.path.isdir(f'{apppath}/templates_data'):
                        os.mkdir(f'{apppath}/templates_data')
                    shutil.copytree(f'{modulepath}templates/{args["name"]}/data/',
                                    f'{apppath}/templates_data/{args["name"]}')
                except  FileExistsError:
                    pass
                except FileNotFoundError:
                    pass
                update()
                return print(f'{GREEN}Template {args["name"]} successfully installed{RESET}')
            except FileExistsError:
                return print(f'{BLUE}Template {args["name"]} has already installed{RESET}')
            except FileNotFoundError:
                return print(f'{BLUE}Template {args["name"]} not found{RESET}')
        elif sys.argv[1].lower() == 'migrate_app':
            args = get_args(['name'], ' '.join(sys.argv[2:]))
            if 'name' not in args.keys():
                return print(f'{RED}The app`s name is not specified{RESET}')
            ensure_appname = replace_all(args['name'], '-&$#!@%^().,', '_')
            if not os.path.isdir(ensure_appname):
                return print(f'{BLUE}The app named {args["name"]} does not exist{RESET}')
            with open(f'{ensure_appname}/__init__.py', 'w') as f:
                data = """import sys, importlib
if '%appname%.app' not in sys.modules.keys():
    from %appname%.app import dp
else:
    dp = importlib.reload(sys.modules['%appname%.app']).dp
""".replace('%appname%', ensure_appname)
                f.write(data)
            with open(f'{ensure_appname}/config.json', 'w') as f:
                data = """
{
	"debug": false
}
"""
                f.write(data)
            print(f'{GREEN}App successfully migrated{RESET}')
        else:
            return print(f'{RED}Command {sys.argv[1].lower()} is not exists{RESET}')
    else:
        return print(f'{RED}Command was not specified{RESET}')


if __name__ == '__main__':
    main()