from typing import IO, Any
import importlib.util
import os
import shutil
import zipfile
import io
import enum
import asyncio


class PackageType(enum.Enum):
    ZIP = 'zip'
    FILESYSTEM = 'filesystem'


class _SyncStorageApi:
    def __init__(
        self,
        root: str = '',
        package: str | None = None,
        *,
        zip_file: bool | str = False
    ):
        if not os.path.exists(root) and not os.path.isdir(root) and not package and not zip_file:
            os.makedirs(root, exist_ok=True)

        self.root = root if package else os.path.abspath(root)
        self.package = package
        self._package_type = None
        self._package_path = ''
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
        elif zip_file:
            self._package_zip = zip_file
            self._package_type = PackageType.ZIP

    def __call__(self, path: str, mode: str, encoding: str = 'utf-8') -> _SyncStorageIO:
        return _SyncStorageIO(self._get_path(path), mode, encoding, self.package, self._package_type, self._package_zip)

    def _check_writable(self) -> bool:
        return not self._package_zip

    def _require_writable(self):
        if not self._check_writable():
            raise OSError("Filesystem is readonly")

    def isfile(self, path: str) -> bool:
        if not self._package_zip:
            return os.path.isfile(self._get_path(path))
        else:
            with zipfile.ZipFile(self._package_zip) as zf:
                if self._get_path(path) in [info.filename for info in zf.infolist() if not info.is_dir()]:
                    return True
            return False

    def isdir(self, path: str) -> bool:
        if self._package_type != PackageType.ZIP:
            return os.path.isdir(self._get_path(path))
        else:
            with zipfile.ZipFile(self._package_zip) as zf:
                if self._get_path(path) in [info.filename.strip('/').strip() for info in zf.infolist() if info.is_dir()]:
                    return True
            return False

    def listdir(self, path: str) -> list[str]:
        if self._package_type != PackageType.ZIP:
            return os.listdir(self._get_path(path))
        else:
            with zipfile.ZipFile(self._package_zip) as zf:
                _path = self._get_path(path).strip('/')
                return list({
                    name.strip('/').removeprefix(_path).strip('/').strip().split('/')[0]
                    for name in zf.namelist()
                    if name.strip('/').startswith(_path) and name.removeprefix(_path).strip('/').strip()
                })

    def mkdir(self, path: str, mode: int = 0o700):
        self._require_writable()
        os.mkdir(os.path.join(self._package_path, self._get_path(path)), mode)

    def makedirs(self, path: str, mode: int = 0o700, exist_ok: bool = True):
        self._require_writable()
        os.makedirs(self._get_path(path), mode, exist_ok)

    def remove(self, path: str):
        self._require_writable()
        os.remove(self._get_path(path))

    def rmtree(self, path: str):
        self._require_writable()
        shutil.rmtree(self._get_path(path))

    def _get_path(self, path: str, add_package_path: bool = True) -> str:
        if self.package is None:
            return os.path.join(self.root, path.lstrip('/')).replace('\\', '/').replace('//', '/').rstrip('/.').rstrip('/')
        elif self._package_type == PackageType.FILESYSTEM:
            if add_package_path:
                return os.path.join(self._package_path, self.root, path.lstrip('/')).replace('\\', '/').replace('//', '/').rstrip('/.').rstrip('/')
            else:
                return os.path.join(self.root, path.lstrip('/')).replace('\\', '/').replace('//', '/').rstrip('/.').strip('/')
        else:
            return f"{self.package}/{self.root}/{path.lstrip('/')}".replace('\\', '/').replace('//', '/').rstrip('/.').strip('/').replace('/./', '/')

    def substorage(self, path: str) -> _SyncStorageApi:
        return _SyncStorageApi(self._get_path(path, add_package_path=False), self.package, zip_file=self._package_zip if self._package_zip else False)


class _SyncStorageIO:
    def __init__(
        self,
        path: str,
        mode: str,
        encoding: str = 'utf-8',
        package: str | None = None,
        _package_type: PackageType | None = None,
        _package_zip: str | None = None
    ):
        self.path = path
        self.mode = mode
        self.encoding = encoding
        self.package = package
        self._package_type = _package_type
        self._package_zip = _package_zip
        self.io = None

    def __enter__(self) -> IO:
        kwargs = {} if 'b' in self.mode else {'encoding': self.encoding}
        if self._package_type == PackageType.ZIP:
            with zipfile.ZipFile(self._package_zip) as zf:
                if 'b' in self.mode:
                    self.io = zf.open(self.path, self.mode.replace('b', ''), **kwargs)
                else:
                    self.io = io.TextIOWrapper(zf.open(self.path, self.mode), **kwargs)
        else:
            self.io = open(self.path, self.mode, **kwargs)
        return self.io

    def __exit__(self, _type, value, traceback):
        self.io.close()

    def __getattr__(self, __name: str, /):
        return self.io.__getattribute__(__name)

class StorageApi:
    def __init__(
        self,
        root: str = '',
        package: str | None = None,
        *,
        zip_file: bool | str = False,
        executor: Any = None
    ):
        self._sync_storage_api = _SyncStorageApi(root, package, zip_file = zip_file)
        self._executor = executor

    async def _run_in_executor(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, func, *args, **kwargs)
    
    def __call__(self, path: str, mode: str, encoding: str = 'utf-8') -> StorageIO:
        return StorageIO(self._sync_storage_api(path, mode, encoding))
    
    async def isfile(self, path: str) -> bool:
        return await self._run_in_executor(self._sync_storage_api.isfile, path)

    async def isdir(self, path: str) -> bool:
        return await self._run_in_executor(self._sync_storage_api.isdir, path)

    async def listdir(self, path: str) -> list[str]:
        return await self._run_in_executor(self._sync_storage_api.listdir, path)

    async def mkdir(self, path: str, mode: int = 0o700):
        return await self._run_in_executor(self._sync_storage_api.mkdir, path, mode)

    async def makedirs(self, path: str, mode: int = 0o700, exist_ok: bool = True):
        return await self._run_in_executor(self._sync_storage_api.makedirs, path, mode, exist_ok)

    async def remove(self, path: str):
        return await self._run_in_executor(self._sync_storage_api.remove, path)

    async def rmtree(self, path: str):
        return await self._run_in_executor(self._sync_storage_api.rmtree, path)

    def substorage(self, path: str) -> StorageApi:
        return StorageApi(
            self._sync_storage_api._get_path(path, add_package_path=False),
            self._sync_storage_api.package,
            zip_file = self._sync_storage_api._package_zip if self._sync_storage_api._package_zip else False
        )

class StorageIO:
    def __init__(self, _sync_storage_io: _SyncStorageIO, *, executor: Any = None):
        self._sync_storage_io = _sync_storage_io
        self._executor = executor
    
    async def _run_in_executor(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, func, *args, **kwargs)

    async def __aenter__(self) -> IO:
        return await self._run_in_executor(self._sync_storage_io.__enter__)

    async def __aexit__(self, _type, value, traceback):
        return await self._run_in_executor(self._sync_storage_io.__exit__, _type, value, traceback)

    def __getattr__(self, __name: str, /):
        return self._sync_storage_io.__getattribute__(__name)
