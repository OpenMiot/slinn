from slinn import Storage, ApiDispatcher, HttpRender
import slinn


dp = ApiDispatcher()
storage = Storage('templates_data/firstrun')


@dp.get('styles.css')
async def styles():
    return HttpRender('styles.css', storage=storage)


@dp.get('favicon.ico')
async def favicon():
    return HttpRender('favicon.ico', storage=storage)


@dp.get()
async def index():
    return HttpRender('slinn.html', storage=storage, ppdata={
        'version': slinn.version
    })
