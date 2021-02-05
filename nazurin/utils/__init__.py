import asyncio
import logging
import os
from typing import TYPE_CHECKING, List

import aiofiles
import aiofiles.os
import aiohttp

from nazurin.config import TEMP_DIR, UA

from .decorators import retry
from .network import Request

if TYPE_CHECKING:
    from nazurin.models import Image

logger = logging.getLogger('nazurin')

async def downloadImage(img: 'Image', session: aiohttp.ClientSession):
    if os.path.exists(
            img.path) and (await aiofiles.os.stat(img.path)).st_size != 0:
        return
    async with session.get(img.url) as response:
        async with aiofiles.open(img.path, 'wb') as f:
            await f.write(await response.read())

async def downloadImages(imgs: List['Image'], headers=None):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    async with Request(headers=headers) as session:
        tasks = []
        for img in imgs:
            tasks.append(asyncio.create_task(downloadImage(img, session)))
        await asyncio.gather(*tasks)
