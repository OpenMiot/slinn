from slinn.utils import wrap_in_quotes
from slinn import _


class SlinnApiException(Exception): ...

class AppExistsException(SlinnApiException):
    def __init__(self, name):
        super().__init__(_('an app named {name} exists').format(name = wrap_in_quotes(name)))

class AppNotExistException(SlinnApiException):
    def __init__(self, name):
        super().__init__(_('an app named {name} does not exist').format(name = wrap_in_quotes(name)))

class AppNameIsNotValidException(SlinnApiException):
    def __init__(self, name):
        super().__init__(_('an app`s name {name} is not valid').format(name = wrap_in_quotes(name)))

class TemplateNotExistsException(SlinnApiException):
    def __init__(self, name):
        super().__init__(_('a template named {name} does not exist').format(name = wrap_in_quotes(name)))
