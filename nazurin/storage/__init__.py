"""Nazurin storage drivers and storage manager."""
import asyncio
import importlib

from nazurin.config import STORAGE
from nazurin.utils import logger

class Storage(object):
    """Storage manager."""
    disks = list()

    def load(self):
        """Dynamically load all storage drivers."""
        for driver_name in STORAGE:
            driver = importlib.import_module('nazurin.storage.' +
                                             driver_name.lower())
            self.disks.append(getattr(driver, driver_name)())
        logger.info("Storage loaded")

    async def store(self, files):
        tasks = []
        for disk in self.disks:
            tasks.append(disk.store(files))
        await asyncio.gather(*tasks)
        logger.info('Storage completed')
