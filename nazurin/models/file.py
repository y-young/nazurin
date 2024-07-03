import os
import pathlib
from dataclasses import dataclass
from typing import Optional

import aiofiles
import aiofiles.os

from nazurin.config import STORAGE_DIR, TEMP_DIR
from nazurin.utils import logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.helpers import (
    ensure_existence_async,
    sanitize_filename,
    sanitize_path,
)
from nazurin.utils.network import NazurinRequestSession


@dataclass
class File:
    name: str
    url: str = None
    _destination: str = ""

    def __post_init__(self):
        self.name = sanitize_filename(self.name)

    @property
    def path(self) -> str:
        """
        Path to the file in temporary directory.
        """
        return os.path.join(TEMP_DIR, self.name)

    @property
    def destination(self) -> pathlib.Path:
        """
        Destination directory in storage, without file name,
        as relative path to `STORAGE_DIR` (should not begin with `/`),
        e.g. `Pixiv/Artist`.
        """
        return pathlib.Path(STORAGE_DIR, self._destination)

    @destination.setter
    def destination(self, value: str):
        self._destination = sanitize_path(value)

    async def size(self) -> Optional[int]:
        """
        Get file size in bytes
        """

        if os.path.exists(self.path):
            stat = await aiofiles.os.stat(self.path)
            return stat.st_size
        return None

    async def exists(self) -> bool:
        return (
            os.path.exists(self.path)
            and (await aiofiles.os.stat(self.path)).st_size != 0
        )

    @network_retry
    async def download(self, session: NazurinRequestSession) -> Optional[int]:
        if await self.exists():
            logger.info("File {} already exists", self.path)
            return await self.size()
        await ensure_existence_async(TEMP_DIR)
        logger.info("Downloading {} to {}...", self.url, self.path)
        await session.download(self.url, self.path)
        size = await self.size()
        logger.info("Downloaded to {}, size = {}", self.path, size)
        return size
