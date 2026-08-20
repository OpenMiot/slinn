from ...exceptions import EndpointNotFound
from slinn.net import Endpoint
from slinn.net.http.responses import HttpResponse
from slinn.net.http.filters import AnyFilter
from typing import Callable, Iterable
from slinn import _, version


class HCRouter:

    """
    Class for handling HTTP-codes
    """

    def __init__(self) -> None:
        self.functions = {}
        self.add_many(
            '100 Continue',
            '101 Switching Protocols',
            '102 Processing',
            '103 Early Hints',
            '200 OK',
            '201 Created',
            '202 Accepted',
            '203 Non-Authoritative Information',
            '205 Reset Content',
            '206 Partial Content',
            '207 Multi-Status',
            '208 Already Reported',
            '226 IM Used',
            '300 Multiple Choices',
            '301 Moved Permanently',
            '302 Found',
            '303 See Other',
            '304 Not Modified',
            '307 Temporary Redirect',
            '308 Permanent Redirect',
            '400 Bad Request',
            '401 Unauthorized',
            '402 Payment Required',
            '403 Forbidden',
            '404 Not Found',
            '405 Method Not Allowed',
            '406 Not Acceptable',
            '407 Proxy Authentification Required',
            '408 Request Timeout',
            '409 Conflict',
            '410 Gone',
            '411 Length Required',
            '412 Precondition Failed',
            '413 Payload Too Large',
            '414 URI Too Long',
            '415 Unsupported Media Type',
            '416 Range Not Satisfiable',
            '417 Expectation Failed',
            '418 I\'m a teapot',
            '421 Misdirected Request',
            '422 Unprocessable Content',
            '423 Locked',
            '424 Failed Dependency',
            '425 Too Early',
            '426 Upgrade Required',
            '428 Precondition Required',
            '429 Too Many Requests',
            '431 Request Header Fields Too Large',
            '451 Unavaliable For Legal Reasons',
            '500 Internal Server Error',
            '501 Not Implemented',
            '502 Bad Gateway',
            '503 Service Unavailable',
            '504 Gateway Timeout',
            '505 HTTP Version Not Supported',
            '506 Variant Also Negotiates',
            '507 Insufficient Storage',
            '508 Loop Detected',
            '510 Not Extended',
            '511 Network Authentification Required'
        )

        @self(204)
        async def endpoint():
            return HttpResponse('', status = '204 No Content')

    def __getitem__(self, key: int) -> Endpoint:
        if str(key) in self.functions:
            return Endpoint(AnyFilter, self.functions[str(key)])
        raise EndpointNotFound(f'HTTP-code {key} does not exist')

    def __call__(self, code: int) -> Callable[[Callable], Callable]:
        def wrapper(func):
            self.functions[str(code)] = func
            return func
        return wrapper

    def add_many(self, *statuses: str):
        for status in statuses:
            self.add_status(status)

    def add_status(self, status: str):
        code, *message = status.split()
        @self(int(code))
        async def endpoint():
            return HttpResponse(
                (    
                    '<!DOCTYPE html>\r\n'
                    f'<html><head><title>{' '.join(message)}</title></head>'
                    f'<body align="center"><h1>{status}</h1><hr>{version}</body></html>'
                ),
                status = status,
                content_type = 'text/html'
            )
