from typing import IO, Optional
import importlib.util
import importlib.resources as ir
import os
import shutil
import zipfile
import io
import enum


class PackageType(enum.Enum):
    ZIP = 'zip'
    FILESYSTEM = 'filesystem'


class Storage:
    def __init__(self, root, package: Optional[str] = None):
        if not os.path.exists(root) and not os.path.isdir(root):
            os.makedirs(root, exist_ok=True)
        self.root = root
        self.ctx = {}
        self.package = package
        self._package_type = None
        self._package_path = None
        self._package_spec = None
        self._package_zip = None

        if package is not None:
            spec = importlib.util.find_spec(package)
            if spec is None:
                raise ImportError(f"Package {package} not found")
            self._package_spec = spec
            if spec.origin and '.zip' in spec.origin:
                self._package_type = PackageType.ZIP
                self._package_zip = spec.origin.split('.zip')[0] + '.zip'
            else:
                self._package_type = PackageType.FILESYSTEM
                self._package_path = spec.submodule_search_locations[0]
        else:
            os.makedirs(root, exist_ok=True)

    def __call__(self, path, mode, encoding='utf-8'):
        return StorageIO(self.get_path(path), mode, encoding, self.package, self._package_type, self._package_zip)

    def _check_writable(self) -> bool:
        return not self._package_zip

    def _require_writable(self):
        if not self._check_writable():
            raise IOError("Filesystem is readonly")

    def isfile(self, path):
        if not self._package_zip:
            return os.path.isfile(self.get_path(path))
        else:
            with zipfile.ZipFile(self._package_zip) as zf:
                if self.get_path(path) in [info.filename for info in zf.infolist() if not info.is_dir()]:
                    return True
            return False

    def isdir(self, path):
        if not self._package_zip:
            return os.path.isdir(self.get_path(path))
        else:
            with zipfile.ZipFile(self._package_zip) as zf:
                if self.get_path(path) in [info.filename for info in zf.infolist() if info.is_dir()]:
                    return True
            return False

    def listdir(self, path):
        if not self._package_zip:
            return os.listdir(self.get_path(path))
        else:
            with zipfile.ZipFile(self._package_zip) as zf:
                _path = self.get_path(path).strip('/')
                return list(set([
                    name.strip('/').removeprefix(_path).strip('/').strip()
                    for name in zf.namelist()
                    if name.strip('/').startswith(_path) and name.removeprefix(_path).strip('/').strip()
                ]))

    def mkdir(self, path, mode=0o700):
        self._require_writable()
        os.mkdir(self.get_path(path), mode)

    def makedirs(self, path, mode=0o700, exist_ok=True):
        self._require_writable()
        os.makedirs(self.get_path(path), mode, exist_ok)

    def remove(self, path):
        self._require_writable()
        os.remove(self.get_path(path))

    def rmtree(self, path):
        self._require_writable()
        shutil.rmtree(self.get_path(path))

    def get_path(self, path: str) -> str:
        if self.package is None:
            return os.path.join(self.root, path.lstrip('/')).replace('\\', '/').replace('//', '/').rstrip('/.').strip('/')
        if self._package_type == PackageType.FILESYSTEM:
            return os.path.join(self._package_path, self.root, path.lstrip('/')).replace('\\', '/').replace('//', '/').rstrip('/.').strip('/')
        else:
            return f"{self.package}/{self.root}/{path.lstrip('/')}".replace('\\', '/').replace('//', '/').rstrip('/.').strip('/').replace('/./', '/')

    def substorage(self, path):
        return Storage(self.get_path(path), self.package)


class StorageIO:
    def __init__(self, path, mode, encoding='utf-8', package: Optional[str] = None, _package_type: Optional[PackageType] = None
                 , _package_zip: Optional[str] = None):
        self.path = path.replace('//', '/')
        self.mode = mode
        self.encoding = encoding
        self.package = package
        self._package_type = _package_type
        self._package_zip = _package_zip
        self.io = None

    def __enter__(self) -> IO:
        kwargs = {} if 'b' in self.mode else {'encoding': self.encoding}
        if self.package:
            if self._package_type == PackageType.FILESYSTEM:
                self.io = ir.files(self.package).joinpath(self.path).open(self.mode, **kwargs)
            elif self._package_type == PackageType.ZIP:
                if 'b' in self.mode:
                    with zipfile.ZipFile(self._package_zip) as zf:
                        self.io = zf.open(self.path, self.mode.replace('b', ''), **kwargs)
                else:
                    with zipfile.ZipFile(self._package_zip) as zf:
                        self.io = io.TextIOWrapper(zf.open(self.path, self.mode), **kwargs)
        else:
            self.io = open(self.path, self.mode, **kwargs)
        return self.io

    def __exit__(self, _type, value, traceback):
        self.io.close()

    def __getattr__(self, __name: str):
        return self.io.__getattribute__(__name)
