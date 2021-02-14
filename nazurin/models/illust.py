import asyncio
from dataclasses import dataclass, field
from typing import List

from nazurin.config import TEMP_DIR
from nazurin.utils import Request
from nazurin.utils.helpers import ensureExistence

from .caption import Caption
from .file import File
from .image import Image

@dataclass
class Illust:
    images: List[Image] = field(default_factory=list)
    caption: Caption = field(default_factory=Caption)
    metadata: dict = field(default_factory=dict)
    files: List[File] = field(default_factory=list)

    @property
    def all_files(self) -> List[File]:
        return self.images + self.files

    async def download(self, **kwargs):
        ensureExistence(TEMP_DIR)
        async with Request(**kwargs) as session:
            tasks = []
            for file in self.all_files:
                if not file.url:
                    continue
                tasks.append(asyncio.create_task(file.download(session)))
            await asyncio.gather(*tasks)
