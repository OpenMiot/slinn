from slinn import ApiDispatcher, AnyFilter, HttpResponse, HttpRedirect, HttpJSONResponse


dp = ApiDispatcher()


@dp.get('api')
async def api(request):
    return HttpJSONResponse(status='ok')

@dp.get()
@dp.get('index')
async def index(request):
    return HttpRedirect('/helloworld')


@dp(AnyFilter)
async def helloworld(request):
     return HttpResponse('Hello world!')