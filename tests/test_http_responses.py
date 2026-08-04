from slinn.net.http.responses import *
from slinn import version


def test_http_response_chunk():
    assert HttpResponseChunk('test').make() == b'test'

def test_http_response_header_base():
    http =  b'HTTP/1.1 200 OK\r\n'
    http += b'Content-Type: text/plain; charset=utf-8\r\n'
    http += b'Server: ' + version.encode() + b'\r\n'
    http += b'Content-Encoding: gzip\r\n'
    http += b'Connection: Keep-Alive\r\n'
    http += b'\r\n'
    print(HttpResponseHeader().make())
    assert HttpResponseHeader().make() == http

def test_http_response_header_custom_data():
    http = b'HTTP/1.1 200 OK\r\n'
    http += b'Content-Type: text/html; charset=utf-8\r\n'
    http += b'Server: ' + version.encode() + b'\r\n'
    http += b'Access-Control-Allow-Origin: *\r\n'
    http += b'Content-Encoding: gzip\r\n'
    http += b'Connection: Keep-Alive\r\n'
    http += b'\r\n'
    assert HttpResponseHeader([
        ('Access-Control-Allow-Origin', '*' )
    ], content_type='text/html; charset=utf-8').make() == http

def test_http_response_header_custom_startline():
    http = b'HTTP/1.0 403 Forbidden\r\n'
    http += b'Content-Type: text/plain; charset=utf-8\r\n'
    http += b'Server: ' + version.encode() + b'\r\n'
    http += b'Content-Encoding: gzip\r\n'
    http += b'Connection: close\r\n'
    http += b'\r\n'
    assert HttpResponseHeader(status='403 Forbidden').make(version='HTTP/1.0') == http
