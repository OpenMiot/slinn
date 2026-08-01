from slinn.utils import lazy_exporter
from functools import partial


__getattr__ = partial(lazy_exporter, __name__, {
    'TcpClient': 'tcp_client',
    'TcpFilter': 'tcp_filter',
    'TcpPipe': 'tcp_pipe',
    'TcpRequest': 'tcp_request',
    'TcpResponse': 'tcp_response',
    'TcpRouterProtocol': 'tcp_router_protocol',
    'TcpServer': 'tcp_server',
})
