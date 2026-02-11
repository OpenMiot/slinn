from slinn import Dispatcher, LinkFilter, AnyFilter, HttpResponse, ApiDispatcher, Render
import slinn

def read(filename):
    file = open(filename, 'r', encoding='utf-8')
    data = file.read()
    file.close()
    return data
 
dp = ApiDispatcher()

@dp.get('styles.css')
def styles():
    return Render('templates_data/firstrun/styles.css')

@dp.get('favicon.ico')
def favicon():
    return Render('templates_data/firstrun/favicon.ico')
                       
@dp.get()
def index():
    return Render('templates_data/firstrun/slinn.html', ppdata={
        'version': slinn.version
    })
