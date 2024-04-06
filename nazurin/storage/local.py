import asyncio
import os
import shutil
from typing import List

from nazurin.config import DATA_DIR, STORAGE_DIR
from nazurin.models import File
from nazurin.utils.decorators import async_wrap
from nazurin.utils.helpers import ensure_existence, ensure_existence_async


class Local:
    def __init__(self):
        ensure_existence(os.path.join(DATA_DIR, STORAGE_DIR))

    @staticmethod
    @async_wrap
    def move_file(file: File):
        shutil.copyfile(
            file.path,
            os.path.join(os.path.join(DATA_DIR, file.destination), file.name),
        )

    async def store(self, files: List[File]):
        destinations = {file.destination for file in files}
        tasks = [
            ensure_existence_async(os.path.join(DATA_DIR, destination))
            for destination in destinations
        ]
        await asyncio.gather(*tasks)

        tasks = [self.move_file(file) for file in files]
        await asyncio.gather(*tasks)
        return True
