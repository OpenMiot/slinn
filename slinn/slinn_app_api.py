from slinn import Storage
import json


class SlinnAppAPI:
    def __init__(self, path):
        self.path = path
        self.root = Storage(self.path)
    
    @property
    def config(self):
        with self.root('config.json', 'r') as config:
            return json.load(config)
