from slinn import Storage
from typing import Optional
import json


class SlinnAppAPI:
    def __init__(self, path, package: Optional[str] = None):
        self.path = path
        self.root = Storage(self.path, package)

    @property
    def config(self):
        with self.root('config.json', 'r') as config:
            return json.load(config)
