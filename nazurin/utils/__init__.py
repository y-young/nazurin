import asyncio
import logging
import os
from typing import TYPE_CHECKING, List, Optional

import aiofiles
import aiofiles.os
import aiohttp

from nazurin.config import TEMP_DIR, UA

from .decorators import retry
from .network import Request

if TYPE_CHECKING:
    from nazurin.models import File

logger = logging.getLogger('nazurin')

async def downloadFile(file: 'File', session: aiohttp.ClientSession):
    if os.path.exists(
            file.path) and (await aiofiles.os.stat(file.path)).st_size != 0:
        return
    async with session.get(file.url) as response:
        async with aiofiles.open(file.path, 'wb') as f:
            await f.write(await response.read())

async def downloadFiles(files: List['File'], headers: Optional[dict] = None):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    async with Request(headers=headers) as session:
        tasks = []
        for file in files:
            tasks.append(asyncio.create_task(downloadFile(file, session)))
        await asyncio.gather(*tasks)
