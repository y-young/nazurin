from dataclasses import dataclass
from random import random

from models import Image

from .config import IMG_PROXY

@dataclass
class PixivImage(Image):
    @property
    def display_url(self):
        # use reverse proxy to avoid strange problems
        return self.chosen_url.replace('i.pximg.net',
                                       IMG_PROXY)  # + '?' + str(random())
