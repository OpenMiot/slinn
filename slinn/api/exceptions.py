from slinn import _


class SlinnApiException(Exception): ...

class AppExistsException(SlinnApiException):
    def __init__(self, name):
        super().__init__(_('an app named \'{name}\' exists').format(name = name))

class AppNotExistException(SlinnApiException):
    def __init__(self, name):
        super().__init__(_('an app named \'{name}\' does not exist').format(name = name))

class AppNameIsNotValid(SlinnApiException):
    def __init__(self, name):
        super().__init__(_('an app`s name \'{name}\' is not valid').format(name = name))

class AppNameIsNotSpecified(SlinnApiException):
    def __init__(self):
        super().__init__(_('an app`s name is not specified'))
