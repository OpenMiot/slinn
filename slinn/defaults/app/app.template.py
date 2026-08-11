from slinn.net.http import HttpRouter, HttpRequest
from . import app, project


router = HttpRouter()


@router.get('/')
async def index(request: HttpRequest):
    return 'Hello, World!'
