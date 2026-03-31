# Slinn

**Slinn is an HTTP server framework**

![License](https://img.shields.io/github/license/OpenMiot/slinn)
![GitHub top language](https://img.shields.io/github/languages/top/OpenMiot/slinn)

![GitHub Release](https://img.shields.io/github/v/release/OpenMiot/slinn)
![GitHub repo size](https://img.shields.io/github/repo-size/OpenMiot/slinn)
![GitHub Repo stars](https://img.shields.io/github/stars/OpenMiot/slinn)


### Simple example
```python
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

```

### Begin project
#### Standart
```bash
python3 -m slinn create helloworld
cd helloworld
venv/bin/python manage.py create localhost host=localhost host=127.0.0.1
venv/bin/python manage.py run 
```

Insert example into localhost/app.py file
> [!TIP]
> Instead of use example, create app from template `py manage.py template example` on Windows and `venv/bin/python manage.py template example` on Unix-like OSes

Excepted output
```
helloworld $ venv/bin/python manage.py run
Loading config...
Apps: firstrun
Debug mode enabled
Smart navigation enabled

Starting server...
HTTP server is available on http://localhost:8080/
```

To config project you should edit `./project.json`

To config app you should edit `./%app%/config.json`

#### Classic
##### Unix-like (Linux, MacOS, FreeBSD...):
```bash 
mkdir helloworld 
cd helloworld
python3 -m venv venv
venv/bin/activate
```

##### Windows:
```batch
mkdir helloworld 
cd helloworld
python3 -m venv venv
venv\Scripts\activate
```

Insert example into `./example.py` and add following code:
```
from slinn import AsyncServer
import asyncio
asyncio.run(AsyncServer(dp).listen(Address(8080)))
```
then write `python example.py`

Excepted output
```
helloworld $ venv/bin/python example.py
HTTP server is available on http://localhost:8080/
```
