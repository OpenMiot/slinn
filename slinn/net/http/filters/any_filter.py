from .filter import Filter


AnyFilter = Filter(
    '.*',
    (
        'GET',
        'HEAD',
        'POST',
        'PUT',
        'DELETE',
        'CONNECT',
        'OPTIONS',
        'TRACE',
        'PATCH'
    )
)