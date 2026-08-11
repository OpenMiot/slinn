from slinn.net.http.responses import *
from slinn.net.http import HttpRequest
from slinn.net.tcp import TcpPipe
from slinn.net.address import Address, TransportProtocol
from slinn import version
import asyncio
import pytest


@pytest.fixture
def sample_request() -> HttpRequest:
    event_loop = asyncio.new_event_loop()
    request = HttpRequest(
        event_loop,
        'GET / HTTP/1.1',
        Address(0, TransportProtocol.TCP),
        TcpPipe(event_loop),
        None,
        None
    )
    return request


def test_http_response_chunk(sample_request):
    assert HttpResponseChunk('test').make(sample_request) == b'test'


def describe_http_response_header():
    def base(sample_request):
        http =  b'HTTP/1.1 200 OK\r\n'
        http += b'Content-Type: text/plain; charset=utf-8\r\n'
        http += b'Server: ' + version.encode() + b'\r\n'
        http += b'Content-Encoding: gzip\r\n'
        http += b'Connection: Keep-Alive\r\n'
        http += b'\r\n'
        assert HttpResponseHeader().make(sample_request) == http

    def custom_data(sample_request):
        http = b'HTTP/1.1 200 OK\r\n'
        http += b'Content-Type: text/html; charset=utf-8\r\n'
        http += b'Server: ' + version.encode() + b'\r\n'
        http += b'Access-Control-Allow-Origin: *\r\n'
        http += b'Content-Encoding: gzip\r\n'
        http += b'Connection: Keep-Alive\r\n'
        http += b'\r\n'
        assert HttpResponseHeader([
            ('Access-Control-Allow-Origin', '*' )
        ], content_type='text/html; charset=utf-8').make(sample_request) == http

    def custom_startline(sample_request):
        sample_request.version = 'HTTP/1.0'
        sample_request.connection = 'close'
        http = b'HTTP/1.0 403 Forbidden\r\n'
        http += b'Content-Type: text/plain; charset=utf-8\r\n'
        http += b'Server: ' + version.encode() + b'\r\n'
        http += b'Content-Encoding: gzip\r\n'
        http += b'Connection: close\r\n'
        http += b'\r\n'
        assert HttpResponseHeader(status='403 Forbidden').make(sample_request) == http
