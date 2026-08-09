from datetime import datetime, timedelta
from babel.dates import format_timedelta
from locale import getdefaultlocale
from contextvars import ContextVar
from slinn import utils
from slinn import exceptions
import os
import sys
import inspect
import warnings
import gettext


root = os.path.dirname(inspect.getfile(sys.modules[__name__]))

ctx_translations: ContextVar = ContextVar("translations")

def _(text: str) -> str:
    try:
        return ctx_translations.get().gettext(text)
    except LookupError:
        try:
            lang = (getdefaultlocale()[0] or 'en_US').split('_')[0]
            fallback_trans = gettext.translation('messages', localedir=root+'/locales', languages=[lang], fallback=True)
            return fallback_trans.gettext(text)
        except Exception:
            return text

__PD = datetime(2026, 8, 10)

VERSION = {
    'name': 'Slinn',
    'codename': 'Flux',
    'version': {
        'major': 3,
        'minor': 0,
        'patch': 0,
        'type': 'alpha',
        'revision': 8
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

if VERSION['is_eap'] and datetime.now() > VERSION['dies_at']:
    exit(f'Slinn`s EAP version has expired ({format_timedelta(datetime.now() - VERSION['dies_at'], locale=getdefaultlocale()[0])}).\n'
         f'Current version: {version}\n'
         f'You need to upgrade to a newer EAP version or to a release:\n'
         f' - Release: {VERSION['release_install']}\n'
         f' - EAP: {VERSION['eap_install']}\n\n')

if VERSION['may_incompatible']:
    warnings.warn(
        message = _('Slinn`s EAP version may be incompatible with future releases. Don`t use it in prod'),
        category = exceptions.IncompatibleVersion,
        skip_file_prefixes = (os.path.dirname(__name__), )
    )

from slinn.i_middleware import IMiddleware
from slinn.preprocessor import Preprocessor
from slinn.ftdispatcher import FTDispatcher
from slinn.hcdispatcher import HCDispatcher
from slinn.dispatcher import Dispatcher
from slinn.migration import Migration
from slinn.template_protocol import TemplateProtocol
