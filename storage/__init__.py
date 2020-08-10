"""Nazurin storage drivers and storage manager."""
import importlib
from config import STORAGE
from utils import logger

class Storage(object):
    """Storage manager."""

    disks = list()

    def __init__(self):
        """Dynamically load all storage drivers."""
        self.load()

    def load(self):
        for driver_name in STORAGE:
            driver = importlib.import_module('storage.' + driver_name.lower())
            self.disks.append(getattr(driver, driver_name)())
        logger.info("Storage loaded")

    def store(self, files):
        for disk in self.disks:
            disk.store(files)
        logger.info('Storage completed')