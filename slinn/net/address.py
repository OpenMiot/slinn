from typing import Optional, Iterable
import socket
import enum


class TransportProtocol(enum.Enum):
    TCP = 'TCP'
    UDP = 'UDP'

_DEFAULT_PORTS = {
    'http': '80/tcp',
    'https': '443/tcp',
    'quic': '443/udp',
    'ws': '80/tcp',
    'wss': '443/tcp'
}


class AddressConfigFactory:
    @staticmethod
    def get_address(**config) -> Address:
        transport_protocol = TransportProtocol(config['port'].split('/')[1].upper())
        return Address(
            port = int(config['port'].split('/')[0]),
            transport_protocol = transport_protocol,
            domains = tuple(config.get('domains', [])),
            protocol = config.get('protocol', transport_protocol.value.lower()),
            tls = config.get('tls', False),
            host = config.get('host', '0.0.0.0')
        )


class Address:
    def __init__(
        self,
        port: int,
        transport_protocol: TransportProtocol,
        host: str = '0.0.0.0',
        domains: Iterable[str] = (),
        protocol: Optional[str] = None,
        tls: bool = False,
    ):
        self.port = port
        self.transport_protocol = transport_protocol
        self.domains = set(domains)
        self.protocol = protocol if protocol else self.transport_protocol.value.lower()
        self.tls = tls
        self.host = host
        self.family, sock_type, proto, cannon_name, sock_addr = socket.getaddrinfo(
            self.host, self.port, socket.AF_UNSPEC, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)[0]
        self.host = sock_addr[0]
        self.domains.add(host)

    def __repr__(self):
        urls = set()

        for domain in self.domains:
            if self.protocol in _DEFAULT_PORTS:
                default_port, default_tp = _DEFAULT_PORTS[self.protocol].split('/')
                if default_port == self.port and default_tp == self.transport_protocol:
                    urls.add(f'{self.protocol}://{domain}')
                    continue
            urls.add(f'{self.protocol}://{domain}:{self.port}')

        return '\n'.join(urls)
