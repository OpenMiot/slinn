from slinn import HCDispatcher, AsyncRequest, HttpResponse


hcdp = HCDispatcher()


@hcdp(404)
async def code_404(request: AsyncRequest):
    await request.respond(HttpResponse, '404 Not Found', status='404 Not Found')

@hcdp(413)
async def code_413(request: AsyncRequest):
    await request.respond(HttpResponse, '413 Content Too Large', status='413 Content Too Large')

@hcdp(400)
async def code_400(request: AsyncRequest):
    await request.respond(HttpResponse, '400 Bad Request', status='400 Bad Request')
