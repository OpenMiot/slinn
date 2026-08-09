
<div align="center">
    <h1>Slinn</h1>
    <b>Slinn is an HTTP server framework</b><br/>
    <img src="https://img.shields.io/github/license/OpenMiot/slinn" alt="License"/>
    <img src="https://img.shields.io/github/languages/top/OpenMiot/slinn" alt="GitHub top language"/>
    <img src="https://img.shields.io/github/v/release/OpenMiot/slinn" alt="GitHub Release"/>
    <img src="https://img.shields.io/github/stars/OpenMiot/slinn" alt="GitHub Repo stars"/>
</div>

### Simple example
```python
from slinn import (
    ApiDispatcher, AnyFilter, AsyncRequest, HttpResponse,
    HttpRedirect, HttpJSONResponse
)


dp = ApiDispatcher()


@dp.get('api/<str method>')
async def api(request: AsyncRequest, method: str) -> HttpResponse:
    return HttpJSONResponse(
        status='ok',
        method=method,
        ip=request.ip
    )

@dp.get()
@dp.get('index')
async def index() -> HttpResponse:
    return HttpRedirect('/helloworld')


@dp(AnyFilter)
async def helloworld() -> HttpResponse:
     return HttpResponse('Hello world!')

```

### Begin project
#### Standart
```bash
slinn-admin create-project www
cd www
venv/bin/activate
slinn create-app localhost host=localhost host=127.0.0.1
```

Insert example into localhost/app.py file, then run `start.bat` or `start.sh` script

> [!TIP]
> Instead of use example, create app from template `slinn template example`

Expected output
```
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

Expected output
```
helloworld $ venv/bin/python example.py
HTTP server is available on http://localhost:8080/
```
