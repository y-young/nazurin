from dataclasses import dataclass, field
from typing import List, Union

from nazurin.config import MAX_PARALLEL_DOWNLOAD
from nazurin.utils import Request
from nazurin.utils.helpers import run_in_pool
from nazurin.utils.network import NazurinRequestSession

from .caption import Caption
from .file import File
from .image import Image


@dataclass
class Illust:
    id: Union[int, str]
    images: List[Image] = field(default_factory=list)
    caption: Caption = field(default_factory=Caption)
    metadata: dict = field(default_factory=dict)
    files: List[File] = field(default_factory=list)

    @property
    def all_files(self) -> List[File]:
        return self.images + self.files

    def has_image(self) -> bool:
        return len(self.images) != 0

    def has_multiple_images(self) -> bool:
        return len(self.images) > 1

    async def download(
        self,
        *,
        request_class: NazurinRequestSession = Request,
        **kwargs,
    ):
        async with request_class(**kwargs) as session:
            files = filter(lambda file: file.url, self.all_files)
            tasks = [file.download(session) for file in files]
            await run_in_pool(tasks, MAX_PARALLEL_DOWNLOAD)
