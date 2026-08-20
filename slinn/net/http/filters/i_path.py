from . import Filter
from slinn.net.http import HttpHeaders
from slinn.exceptions import PatternDoesNotMatch
from slinn import _
import re


class int(int): REGEXP = r'[0-9]+'
class float(float): REGEXP = r'[0-9\.]+'
class str(str): REGEXP = r'[\w\- ]+'


class IPath(Filter):
    def __init__(self, pattern: str, methods: tuple[str, ...] = ('GET', 'POST')):
        super().__init__(pattern, methods)
        self.types = {}
        for a in self.filter.findall(r'<\w+ \w+>'):
            t, n = a[1:-1].split()
            t = eval(t.split()[0])
            self.filter = self.filter.replace(a, '(?P<'+n+'>' + t.REGEXP + ')')
            self.types[n] = t

    def args(self, headers: HttpHeaders) -> dict:
        args = re.search(self.filter, headers.link)
        if args is None:
            raise PatternDoesNotMatch(
                _('A path matching template "{pattern}", but path "{path}" was given"').format(
                    pattern = self.filter.pattern,
                    path = headers.full_link
                )
            )
        args = args.groupdict()
        return {
            n: self.types[n](args[n])
            for n in args
        }


if __name__ == '__main__':
    f = '/users/<str user>/profile/<int tab>'
    r = '/users/mrybs/profile/104'
    print(IPath(f).check(r, 'GET'))
    print(IPath(f).args(r))
