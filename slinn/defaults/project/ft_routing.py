from slinn import Preprocessor
from slinn.net.http import FTRouter
from slinn.net.http.responses import HttpResponse
import _io # type: ignore
import json


router = FTRouter()
pp = Preprocessor()

@router.by_extension('html')
async def html(file: _io.BufferedReader, ppdata: dict | None = None) -> HttpResponse:
    return HttpResponse(pp.preprocess(file.read().decode(), ppdata if ppdata else {}), content_type='text/html')

@router.by_extension('css')
async def css(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='text/css')

@router.by_extension('js')
async def js(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='text/javascript')

@router.by_extension('png')
async def png(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='image/png')

@router.by_extension('json')
async def json_handler(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(json.dumps(json.load(file), ensure_ascii=False), content_type='application/json')

@router.by_extension('xml')
async def xml_handler(file: _io.BufferedReader) -> HttpResponse:
    return HttpResponse(file.read(), content_type='application/xml')
