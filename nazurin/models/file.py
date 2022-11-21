import os
from dataclasses import dataclass

import aiofiles
import aiofiles.os
import aiohttp

from nazurin.config import TEMP_DIR
from nazurin.utils.decorators import network_retry
from nazurin.utils.helpers import ensure_existence, sanitize_filename

@dataclass
class File:
    name: str
    url: str = None

    def __post_init__(self):
        self.name = sanitize_filename(self.name)

    @property
    def path(self) -> str:
        return os.path.join(TEMP_DIR, self.name)

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
        ensure_existence(TEMP_DIR)
        async with session.get(self.url) as response:
            async with aiofiles.open(self.path, 'wb') as f:
                await f.write(await response.read())
