import importlib
from config import STORAGE

class Storage(object):
    def __init__(self):
        self.disks = list()
        self.load()

    def load(self):
        for driver_name in STORAGE:
            driver = importlib.import_module('storage.' + driver_name.lower())
            self.disks.append(getattr(driver, driver_name))

    def store(self, files):
        for disk in self.disks:
            disk().store(files)