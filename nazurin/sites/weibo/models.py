from dataclasses import dataclass

from nazurin.models import Illust, Image


@dataclass
class WeiboImage(Image):
    referer: str = None

    async def size(self, **kwargs):
        return await super().size(headers={"Referer": self.referer}, **kwargs)


@dataclass
class WeiboIllust(Illust):
    referer: str = None

    async def download(self, **kwargs):
        await super().download(headers={"Referer": self.referer}, **kwargs)
