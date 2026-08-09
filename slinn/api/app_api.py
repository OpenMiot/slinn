from slinn.api.storage_api import StorageApi
from typing import Optional
from pydantic import BaseModel
import tomllib


class AppConfig(BaseModel):
    class App(BaseModel):
        routers: list[str]
    app: App


class AppAPI:
    def __init__(self, path: str, package: Optional[str] = None):
        self.path = path
        self.root = StorageApi(self.path, package)

    @property
    def config(self) -> AppConfig:
        with self.root('config.toml', 'rb') as config:
            return AppConfig(**tomllib.load(config))
