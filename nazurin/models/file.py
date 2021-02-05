import os
from dataclasses import dataclass

import aiofiles.os

from nazurin.config import TEMP_DIR
from nazurin.utils.helpers import sanitizeFilename

@dataclass
class File:
    name: str
    url: str = None

    def __post_init__(self):
        self.name = sanitizeFilename(self.name)

    @property
    def path(self) -> str:
        return os.path.join(TEMP_DIR, self.name)

    async def size(self):
        if os.path.exists(self.path):
            stat = await aiofiles.os.stat(self.path)
            return stat.st_size
