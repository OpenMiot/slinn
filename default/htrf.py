from slinn import FTDispatcher, Response
import _io # type: ignore


htrf = FTDispatcher()

@htrf.by_extension('html')
def html(file: _io.BufferedReader) -> Response:
    return Response(file.read(), content_type='text/html')

@htrf.by_extension('css')
def css(file: _io.BufferedReader) -> Response:
    return Response(file.read(), content_type='text/css')

@htrf.by_extension('js')
def js(file: _io.BufferedReader) -> Response:
    return Response(file.read(), content_type='text/javascript')

@htrf.by_extension('png')
def png(file: _io.BufferedReader) -> Response:
    return Response(file.read().decode(), content_type='image/png')
