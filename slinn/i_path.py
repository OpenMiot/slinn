from . import Filter
from .exceptions import PatternDoesNotMatch
import re


class int(int): REGEXP = r'[0-9]+'
class float(float): REGEXP = r'[0-9\.]+'
class str(str): REGEXP = r'[\w ]+'


class IPath(Filter):
    def __init__(self, pattern, methods=('GET', 'POST')):
        super().__init__(pattern, methods)
        self.types = {}
        self._pattern = pattern
        for a in re.findall(r'<\w+ \w+>', pattern):
            t, n = a[1:-1].split()
            t = eval(t)
            self.filter = self.filter.replace(a, '(?P<'+n+'>' + t.REGEXP + ')')
            self.types[n] = t

    def args(self, request):
        args = re.search(self.filter, request.link)
        if args is None:
            raise PatternDoesNotMatch(f'A path matching template "{self._pattern}", but path "{request.full_link}" was given"')
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
