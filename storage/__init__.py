import importlib
from config import STORAGE, logger

class Storage(object):
    disks = list()

    def __init__(self):
        self.load()

    def load(self):
        for driver_name in STORAGE:
            driver = importlib.import_module('storage.' + driver_name.lower())
            self.disks.append(getattr(driver, driver_name))
        logger.info("Storage loaded")

    def store(self, files):
        for disk in self.disks:
            disk().store(files)