import os
import shutil
from config import STORAGE_DIR

class Local(object):
    def __init__(self):
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)

    def store(self, files):
        for item in files:
            shutil.copyfile(item.path, os.path.join(STORAGE_DIR, item.name))
        return True