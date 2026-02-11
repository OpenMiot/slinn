from slinn import HttpResponse, Request, Preprocessor
import slinn
from types import TracebackType
import traceback
import sys


class ExceptionResponse(HttpResponse):
    @staticmethod
    def process_traceback(e: Exception, request: Request):
        with slinn.slinn_root('tools/debugger/exception.html', 'r') as f:
            return Preprocessor().preprocess(f.read(), {
                'm1': f'{type(e).__name__} at {request.link}',
                'm2': str(e),
                'method': request.method,
                'full_link': request.full_link,
                'slinn_version': slinn.version,
                'args': ' '.join(sys.argv),
                'executable': sys.executable,
                'frames': list(traceback.extract_tb(e.__traceback__)),
            })

    def __init__(self, e: Exception, request: Request):
        HttpResponse.__init__(self, self.process_traceback(e, request), status='500 Internal Server Error', content_type='text/html', request=request)
