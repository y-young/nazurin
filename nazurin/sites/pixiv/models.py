from dataclasses import dataclass
from random import random

from nazurin.models import Illust, Image

from .config import HEADERS, IMG_PROXY


@dataclass
class PixivImage(Image):
    async def size(self, **kwargs):
        return await super().size(headers=HEADERS, **kwargs)

    async def display_url(self):
        # use reverse proxy to avoid strange problems
        url = await self.chosen_url()
        return url.replace("i.pximg.net", IMG_PROXY) + "?" + str(random())


@dataclass
class PixivIllust(Illust):
    async def download(self, **kwargs):
        await super().download(headers=HEADERS, **kwargs)
