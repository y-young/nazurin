import os
import pathlib
from dataclasses import dataclass

import aiofiles
import aiofiles.os
import aiohttp

from nazurin.config import STORAGE_DIR, TEMP_DIR
from nazurin.utils.decorators import network_retry
from nazurin.utils.helpers import (ensure_existence_async, sanitize_filename,
                                   sanitize_path)

@dataclass
class File:
    name: str
    url: str = None
    _destination: str = ''

    def __post_init__(self):
        self.name = sanitize_filename(self.name)

    @property
    def path(self) -> str:
        """
        Path to the file in temporary directory.
        """
        return os.path.join(TEMP_DIR, self.name)

    @property
    def destination(self) -> os.PathLike:
        """
        Destination directory in storage, without file name,
        as relative path to `STORAGE_DIR` (should not begin with `/`),
        e.g. `Pixiv/Artist`.
        """
        return pathlib.Path(STORAGE_DIR, self._destination)

    @destination.setter
    def destination(self, value: str):
        self._destination = sanitize_path(value)

    async def size(self):
        """
        Get file size in bytes
        """

        if os.path.exists(self.path):
            stat = await aiofiles.os.stat(self.path)
            return stat.st_size

    async def exists(self) -> bool:
        if os.path.exists(self.path) and (await aiofiles.os.stat(
                self.path)).st_size != 0:
            return True
        return False

    @network_retry
    async def download(self, session: aiohttp.ClientSession):
        if await self.exists():
            return True
        await ensure_existence_async(TEMP_DIR)
        async with session.get(self.url) as response:
            async with aiofiles.open(self.path, 'wb') as f:
                await f.write(await response.read())
