from typing import Optional
import socket


class Address:

    """
    IPv4/IPv6 with DNS address structure
    """
    
    def __init__(self, port: int, host: Optional[str] = None):
        self.port = port
        self.host = ''
        if host:
            family, socktype, proto, cannonname, sockaddr = \
                socket.getaddrinfo(host, self.port, socket.AF_UNSPEC, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)[0]
            self.host = sockaddr[0]
        self.domain = host or ''
