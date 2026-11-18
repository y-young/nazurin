import os
from dataclasses import dataclass
from typing import ClassVar

import aiofiles.os
import aiohttp
from PIL import Image as PILImage

from nazurin.models import Illust, Image
from nazurin.utils.decorators import async_wrap

from . import config

REFERER = "https://xfolio.jp/"

FORMAT_EXTENSIONS: ClassVar[dict[str, str]] = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "GIF": ".gif",
}


def get_cookies() -> dict[str, str]:
    if config.SESSION:
        return {"xfolio_session": config.SESSION}
    return {}


@async_wrap
def detect_image_extension(path: str | os.PathLike) -> str | None:
    try:
        with PILImage.open(path) as image:
            return FORMAT_EXTENSIONS.get(image.format or "")
    except OSError:
        return None


@dataclass
class XfolioImage(Image):
    async def size(self, **kwargs):
        headers = {"Referer": REFERER, **kwargs.pop("headers", {})}
        cookies = {**get_cookies(), **(kwargs.pop("cookies", None) or {})}
        return await super().size(headers=headers, cookies=cookies, **kwargs)

    async def download(self, session: aiohttp.ClientSession):
        await super().download(session)
        real_ext = await detect_image_extension(self.path)
        stem, current_ext = os.path.splitext(self.name)
        if real_ext and real_ext.lower() != current_ext.lower():
            old_path = self.path
            self.name = stem + real_ext
            if await aiofiles.os.path.exists(old_path):
                await aiofiles.os.replace(old_path, self.path)


@dataclass
class XfolioIllust(Illust):
    async def download(self, **kwargs):
        headers = {"Referer": REFERER, **kwargs.pop("headers", {})}
        cookies = {**get_cookies(), **(kwargs.pop("cookies", None) or {})}
        await super().download(headers=headers, cookies=cookies, **kwargs)
