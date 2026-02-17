from typing import IO
import os


class Storage:
    def __init__(self, root):
        if not os.path.isdir(root):
            os.makedirs(root, exist_ok=True)
        self.root = root
        self.ctx = {}

    def __call__(self, path, mode, encoding='utf-8'):
        return StorageIO(self.root + '/' + path, mode, encoding)

    def isfile(self, path):
        return os.path.isfile(self.root + '/' + path)


class StorageIO:
    def __init__(self, path, mode, encoding='utf-8'):
        self.path = path
        self.mode = mode
        self.encoding = encoding
        self.io = None

    def __enter__(self) -> IO:
        self.io = open(self.path, self.mode, encoding=self.encoding)
        return self.io

    def __exit__(self, _type, value, traceback):
        self.io.close()

    def __getattr__(self, __name: str):
        return self.io.__getattribute__(__name)
