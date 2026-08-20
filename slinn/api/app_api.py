from typing import Optional, Iterator
from pydantic import BaseModel
from slinn.eda import BaseBus
from slinn.tools.manage.misc import load_module
import tomllib


class AppConfig(BaseModel):
    class App(BaseModel):
        ...
    app: App = App(routers = [])
    class Protocol(BaseModel):
        class HTTP(BaseModel):
            routers: list[str] = []
        http: HTTP | None = HTTP()
    protocol: Protocol | None = Protocol()


class AppApi:
    def __init__(self, name: str, project: 'ProjectAPI', package: Optional[str] = None):
        self.name = name
        self.project = project
        self.storage = project.storage.substorage(name)
        self.config: AppConfig = None

    @staticmethod
    def create_app(name: str) -> AppApi:
        ...

    def load_http_routers(self) -> Iterator:
        files = {}
        for _rn in self.config.protocol.http.routers:
            router_name = _rn.split('.')
            file = f'{self.name}/{'/'.join(router_name[:-1])}.py'
            if file in files:
                files[file].append(router_name[-1])
            else:
                files[file] = [router_name[-1]]
        for file, routers_names in files.items():
            module = load_module(file)
            for router_name in routers_names:
                yield getattr(module, router_name)

    def load_config(self):
        with self.storage('config.toml', 'rb') as config:
            self.config = AppConfig(**tomllib.load(config))
