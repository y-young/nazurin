from dataclasses import dataclass
from random import random

from nazurin.models import Image

from .config import IMG_PROXY

@dataclass
class PixivImage(Image):
    async def display_url(self):
        # use reverse proxy to avoid strange problems
        url = await self.chosen_url()
        return url.replace('i.pximg.net', IMG_PROXY) + '?' + str(random())
