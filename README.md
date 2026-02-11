# Slinn

**Slinn is an HTTP server framework**

![License](https://img.shields.io/github/license/OpenMiot/slinn)

![GitHub Release](https://img.shields.io/github/v/release/OpenMiot/slinn)
![GitHub top language](https://img.shields.io/github/languages/top/OpenMiot/slinn)

![GitHub Repo stars](https://img.shields.io/github/stars/OpenMiot/slinn)
![GitHub watchers](https://img.shields.io/github/watchers/OpenMiot/slinn)
![GitHub forks](https://img.shields.io/github/forks/OpenMiot/slinn)

![GitHub commit activity](https://img.shields.io/github/commit-activity/w/OpenMiot/slinn)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/OpenMiot/slinn)

![GitHub repo size](https://img.shields.io/github/repo-size/OpenMiot/slinn)


### Simple example
```python
from slinn import *


dp = Dispatcher()

@dp(LinkFilter('api'))
def api(request):
    return HttpJSONAPIResponse(status='ok')

@dp(LinkFilter(''))
@dp(LinkFilter('index'))
def index(request):
    return HttpRedirect('/helloworld')


@dp(AnyFilter)
def helloworld(request):
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
Server(dp).listen(Address(8080))
```
then write `python example.py`

Excepted output
```
helloworld $ venv/bin/python example.py
HTTP server is available on http://localhost:8080/
```

### Functions
```python
from slinn import Server

server = Server(*dispatchers: tuple, ssl_cert: str=None, ssl_key: str=None, timeout: float=0.03, max_bytes_per_recieve: int=4096, max_bytes: int=4294967296)  # Main class to run a server
server.address(port: int, domain: str) -> str  # Returns message like 'HTTPS server is available on https://localhost:8080/'
server.reload(*dispatchers: tuple)  # Reloads server
server.listen(address: Address)  # Start listening address

Server(dp_api, dp_gui, ssl_cert='fullchain.pem', ssl_key='privkey.pem')
```

```python
from slinn import Address

address = Address(port: int, host: str=None)  # A structure containing a port and a host; converts dns-address to ip-address

Address(443, 'google.com') <-> Address(443, '2a00:1450:4010:c02::71')

# Attributes
address.port  # port
address.host  # ip
address.domain  # non-converted host from constructor
```

```python
from slinn import Dispatcher

dispatcher = Dispatcher(hosts: tuple=None)  # A class that contain many handlers

Dispatcher('localhost', '127.0.0.1', '::1', '::')

# To add handler into dispatcher
@dispatcher(filter: Filter)
def handler(request: Request):
    ...

# handler should return HttpResponse-based object
```

```python
from slinn import Filter, LinkFilter, AnyFilter

_filter = Filter(filter: str, methods: tuple=None)  # This class is used to choose match handler by link; uses regexp
_filter.check(text: str, method: str) -> bool  # Checks for a match by filter

Filter('/user/.+/profile.*')

# LinkFilter inherits from Filter
LinkFilter('user/.+/profile')

# AnyFilter as same as Filter('.*')
```

```python
from slinn import HttpResponse, HttpRedirect, HttpAPIResponse, HttpJSONResponse, HttpJSONAPIResponse

http_response = HttpResponse(payload: any, data: list[tuple[str, any]]=None, status: str='200 OK', content_type: str='text/plain')  # This class is used to convert some data to HTTP code
http_response.set_cookie(key: str, value: any)  # Sets cookie
http_response.make(type: str='HTTP/2.0') -> str  # Makes HTTP code

HttpResponse('<h1>Hello world</h1>', content_type='text/html')

# HttpAPIResponse inherits from HttpResponse
# HttpAPIResponse sets Access-Control-Allow-Origin to '*'

HttpAPIResponse('{"status": "ok", "username": "mrybs"}')

# HttpRedirect inherits from HttpResponse
HttpRedirect(location: str)

HttpRedirect('slinn.miotp.ru')

# HttpJSONResponse for responding JSON 
HttpJSONResponse(**payload: dict)

HttpJSONResponse(status='this action is forbidden', _status='403 Forbidden')

# HttpJSONAPIResponse for responding JSON and it sets Access-Control-Allow-Origin to '*'

HttpJSONAPIResponse(code=43657, until=1719931149)
```

```python
from slinn import Request

request = Request(header: str, body: bytes, client_address: tuple[str, int])  # This structure is used in the dispatcher`s handler
request.parse_http_header(http_header: str)  # Parse HTTP request`s header
request.parse_http_body(http_body: body)  # Parse HTTP request`s body if exists
str(request)  # Convert slinn.Request to info text

# Attributes
request.ip, request.port  # Client`s IP and port
request.method  # HTTP method
request.version  # HTTP version
request.full_link  # Full link(path and params)
request.host  # Requested host
request.user_agent  # Client`s user agent
request.accept  # maybe supported technologies
request.encoding  # Supported encodings
request.language  # Client`s language
request.link  # Link(only path)
request.args  # GET args
request.cookies  # All saved cookies
request.files # Uploaded files
```

```python
from slinn import File

file = File(id: str=None, data: bytes|bytearray=bytearray())

# Attributes
file.id  # File`s id 
file.data  # Binary data
file.headers  # Headers such as Content-Disposition
```
