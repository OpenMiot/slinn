import urllib.parse
from . import File, FTDispatcher, utils


class Request:
    """
    Representation of HTTP request from client
    """

    @staticmethod
    def parse_http_header(http_header: str) -> dict:
        result = {}
        for line in http_header.split('\r\n'):
            key, value = line.split(':')[0], ':'.join(line.split(':')[1:])
            result[key.strip()] = value.strip()
        return result

    @staticmethod
    def parse_http_body(http_body: bytes):
      files = [File()]
      BGNs = [b'-----------------------------', b'------WebKitFormBoundary']
      END = b'--'
      binary = 0
      for line in http_body.split(b'\r\n'):
        if binary != 2:
          if line == b'':
            binary += 1
          elif b':' in line:
            key, value = line.split(b':')[0].decode(), b':'.join(line.split(b':')[1:])
            files[-1].header[key.strip()] = value.strip()
          elif files[-1].id is None:
            if line.startswith(BGNs[0]):
              files[-1].id = line[len(BGNs[0]):]
            elif line.startswith(BGNs[1]):
              files[-1].id = line[len(BGNs[1]):]
          continue
        if files[-1].id is not None:
          if line.startswith(BGNs[0]) and line.endswith(END) and line[len(BGNs[0]):-len(END)] == files[-1].id \
             or line.startswith(BGNs[1]) and line.endswith(END) and line[len(BGNs[1]):-len(END)] == files[-1].id:
            files[-1].data = bytes(files[-1].data[:-2])
            files.append(File())
            binary = 0
            continue
        files[-1].data += line + b'\r\n'
      return {
        'payload': b'',
        'files': files[:-1]
      } if len(files[:-1]) != 0 else {
        'payload': http_body,
        'files': []
      }

    def __init__(self, header: str, body: bytes, client_address: tuple[str, int], connection, server, htrf: FTDispatcher = FTDispatcher()) -> None:
        def get_args(text):
            return {} if text == '' else {pair.split('=')[0]: '='.join(pair.split('=')[1:]) for pair in text.split('&')}

        self.type = header.split('\r\n')[0].strip().split(' ')
        self.header = {'method': self.type[0], 'link': ' '.join(self.type[1:-1]), 'ver': self.type[-1],
                       'data': {'user-agent': '', 'Accept': '', 'Accept-Encoding': '', 'Accept-Language': ''}}
        header = self.parse_http_header(header)
        self.payload = self.parse_http_body(body)['payload']
        self.files = self.parse_http_body(body)['files']
        self.header['data'].update(header)
        self.ip, self.port = client_address[:2]
        self.protocol = self.header['ver'].split('/')[0]
        self.method = self.header['method']
        self.version = self.header['ver']
        self.full_link = urllib.parse.unquote_plus(self.header['link'].replace('+', ' '))
        self.headers = self.header['data']
        self.host = self.header['data']['Host']
        self.user_agent = self.header['data']['User-Agent'] if 'User-Agent' in self.header['data'].keys() else \
            self.header['data']['user-agent']
        self.accept = self.header['data']['Accept'].split(',')
        self.encoding = self.header['data']['Accept-Encoding'].split(',')
        self.language = self.header['data']['Accept-Language'].split(',')
        self.link = self.full_link[:(self.full_link.index('?') if '?' in self.full_link else None)]
        self.args = get_args(
            self.full_link[(self.full_link.index('?') + 1 if '?' in self.full_link else len(self.full_link)):])
        self.cookies = {c.split('=')[0].strip(): c.split('=')[1] for c in
                        self.header['data']['Cookie'].split(';')} if 'Cookie' in self.header['data'] else dict()

        self.__str__ = self.__repr__

        self.connection = connection
        self.server = server
        self.htrf = htrf

    def __repr__(self) -> str:
        return f'[{self.method}] request {self.full_link} from {"" if "." in self.ip else "["}{self.ip}{"" if "." in self.ip else "]"}:{self.port} on {self.host}'

    def respond(self, response_class, *args, **kwargs) -> None:
        made = utils.optional(response_class(*args, **kwargs).make, version = self.version, htrf = self.htrf)
        if made is None:
            return
        self.connection.sendall(made)

    def recv(self, n_bytes: int) -> bytes:
        return self.connection.recv(n_bytes)

# def set_cookie(self, response_class, *args, **kwargs):
# 	self.client_socket.sendall(response_class(*args, **kwargs).make())
# TODO: implement request.set_cookie
