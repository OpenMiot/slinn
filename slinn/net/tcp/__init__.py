from slinn.utils import lazy_exporter
from functools import partial


__getattr__ = partial(lazy_exporter, __name__, {
    'TCPClient': 'tcp_client',
    'TCPFilter': 'tcp_filter',
    'TCPPipe': 'tcp_pipe',
    'TCPRequest': 'tcp_request',
    'TCPResponse': 'tcp_response',
    'TCPRouterProtocol': 'tcp_router_protocol',
    'TCPServer': 'tcp_server',
})
