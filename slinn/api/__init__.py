from slinn.utils import lazy_exporter
from functools import partial


__getattr__ = partial(lazy_exporter, __name__, {
    'ProjectAPI': 'project_api',
    'AppAPI': 'app_api',
    'StorageApi': 'storage_api',
})
