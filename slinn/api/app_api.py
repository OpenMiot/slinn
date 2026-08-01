from slinn.api.storage_api import StorageApi
from typing import Optional
import tomllib


class AppAPI:
    def __init__(self, path: str, package: Optional[str] = None):
        self.path = path
        self.root = StorageApi(self.path, package)

    @property
    def config(self) -> dict:
        with self.root('config.toml', 'rb') as config:
            return tomllib.load(config)
