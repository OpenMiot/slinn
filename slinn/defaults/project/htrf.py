from slinn import FTDispatcher, HttpResponse, Preprocessor
from typing import Optional
import _io # type: ignore
import json


htrf = FTDispatcher()
pp = Preprocessor()

@htrf.by_extension('html')
def html(file: _io.BufferedReader, ppdata: Optional[dict] = None) -> HttpResponse:
    return HttpResponse(pp.preprocess(file.read().decode(), ppdata if ppdata else {}), content_type='text/html')

@htrf.by_extension('css')
def css(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='text/css')

@htrf.by_extension('js')
def js(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='text/javascript')

@htrf.by_extension('png')
def png(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='image/png')

@htrf.by_extension('json')
def json_handler(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(json.dumps(json.load(file), ensure_ascii=False), content_type='application/json')

@htrf.by_extension('xml')
def xml_handler(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='application/xml')
