"""Nazurin storage drivers and storage manager."""

import asyncio
import importlib
from typing import ClassVar, List

from nazurin.config import STORAGE
from nazurin.models import Illust
from nazurin.utils import logger


class Storage:
    """Storage manager."""

    disks: ClassVar[List[object]] = []

    def load(self):
        """Dynamically load all storage drivers."""
        for driver_name in STORAGE:
            driver = importlib.import_module("nazurin.storage." + driver_name.lower())
            self.disks.append(getattr(driver, driver_name)())
        logger.info("Loaded {} storage(s), using: {}", len(self.disks), STORAGE)

    async def store(self, illust: Illust):
        tasks = [disk.store(illust.all_files) for disk in self.disks]
        await asyncio.gather(*tasks)
        logger.info("Storage completed")
