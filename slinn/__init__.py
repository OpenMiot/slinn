from datetime import datetime, timedelta
from babel.dates import format_timedelta
from locale import getdefaultlocale
from functools import partial
from slinn import utils
from slinn import exceptions
import os
import sys
import inspect
import warnings

from slinn.dispatcher import Dispatcher

__getattr__ = partial(utils.lazy_exporter, __name__, {
    'IMiddleware': 'i_middleware',
    'Preprocessor': 'preprocessor',
    'HCDispatcher': 'hcdispatcher',
    'FTDispatcher': 'ftdispatcher',
    'Migration': 'migration',
    'TemplateProtocol': 'template_protocol',
})


__PD = datetime(2026, 8, 8)

VERSION = {
    'name': 'Slinn',
    'codename': 'Flux',
    'version': {
        'major': 3,
        'minor': 0,
        'patch': 0,
        'type': 'alpha',
        'revision': 6
    },
    'dies_at': __PD + timedelta(days=180),
    'is_eap': True,
    'may_incompatible': True,
    'release_install': 'pip install --upgrade slinn',
    'eap_install': 'pip install --upgrade git+https://github.com/OpenMiot/slinn@flux'
}
make_version = lambda ver: f'{ver['major']}.{ver['minor']}.{ver['patch']}' + (
    f'{ver['type'][0]}{ver['revision']}' if ver['revision'] else '')
version = f'{VERSION['name']} {VERSION['codename']} {make_version(VERSION['version'])}'

root = os.path.dirname(inspect.getfile(sys.modules[__name__]))

if VERSION['is_eap'] and datetime.now() > VERSION['dies_at']:
    exit(f'Slinn`s EAP version has expired ({format_timedelta(datetime.now() - VERSION['dies_at'], locale=getdefaultlocale()[0])}).\n'
         f'Current version: {version}\n'
         f'You need to upgrade to a newer EAP version or to a release:\n'
         f' - Release: {VERSION['release_install']}\n'
         f' - EAP: {VERSION['eap_install']}\n\n')

if VERSION['may_incompatible']:
    warnings.warn(
        message = 'Slinn`s EAP version may be incompatible with future releases. Don`t use it in prod',
        category = exceptions.IncompatibleVersion,
        skip_file_prefixes = (os.path.dirname(__name__),)
    )
