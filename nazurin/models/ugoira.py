from dataclasses import dataclass
from typing import Union

from .caption import Caption
from .file import File
from .illust import Illust


@dataclass(init=False)
class Ugoira(Illust):
    video: File = None

    def __init__(
        self,
        id: Union[int, str],
        video,
        caption=None,
        metadata=None,
        files=None,
    ):
        super().__init__(id)
        self.video = video
        self.caption = caption or Caption()
        self.metadata = metadata
        self.files = files or []

    @property
    def all_files(self):
        return [self.video, *self.files]

    def has_image(self) -> bool:
        return self.video is not None
