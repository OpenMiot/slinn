from typing import IO
import os


class Storage:
    def __init__(self, root):
        if not os.path.isdir(root):
            os.makedirs(root, exist_ok=True)
        self.root = root
        self.ctx = {}

    def __call__(self, path, filemode):
        return StorageIO(self.root + '/' + path, filemode)


class StorageIO:
    def __init__(self, path, filemode):
        self.path = path
        self.filemode = filemode
        self.io = None

    def __enter__(self) -> IO:
        self.io = open(self.path, self.filemode)
        return self.io

    def __exit__(self, _type, value, traceback):
        self.io.close()

    def __getattr__(self, __name: str):
        return self.io.__getattribute__(__name)
