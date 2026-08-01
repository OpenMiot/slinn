from slinn.utils import lazy_exporter
from functools import partial


__getattr__ = partial(lazy_exporter, __name__, {
    'ClientProtocol': 'client_protocol',
    'FilterProtocol': 'filter_protocol',
    'PipeProtocol': 'pipe_protocol',
    'RouterProtocol': 'router_protocol',
    'ServerProtocol': 'server_protocol',
})
