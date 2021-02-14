import asyncio
import os
import shutil
from typing import List

from nazurin.config import STORAGE_DIR
from nazurin.models import File
from nazurin.utils.decorators import async_wrap
from nazurin.utils.helpers import ensureExistence

class Local(object):
    def __init__(self):
        ensureExistence(STORAGE_DIR)

    @async_wrap
    def moveFile(self, file: File):
        shutil.copyfile(file.path, os.path.join(STORAGE_DIR, file.name))

    async def store(self, files: List[File]):
        tasks = [self.moveFile(file) for file in files]
        await asyncio.gather(*tasks)
        return True
