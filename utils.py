import asyncio
import logging
import os
import re
from functools import partial, wraps
from html import escape
from mimetypes import guess_type
from pathlib import Path
from typing import TYPE_CHECKING, List

import aiofiles
import aiohttp
import requests
import tenacity
from telethon.helpers import ensure_parent_dir_exists
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl

from config import RETRIES, TEMP_DIR, UA

if TYPE_CHECKING:
    from models import Image

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger('nazurin')
retry = tenacity.retry(stop=tenacity.stop_after_attempt(5),
                       before=tenacity.before_log(logger, logging.INFO))

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def chat_action(action: str):
    """Sends `action` while processing."""
    def decorator(func):
        @wraps(func)
        async def wrapped_func(event, *args, **kwargs):
            async with event.client.action(event.chat, action):
                return await func(event, *args, **kwargs)

        return wrapped_func

    return decorator

@chat_action('photo')
async def sendPhotos(event, imgs: List['Image'], details=None):
    if details is None:
        details = dict()
    media = list()
    # if len(imgs) > 10:
    #     # TODO
    #     imgs = imgs[:10]
    #     await event.reply('Notice: Too many pages, sending only 10 of them')

    caption = str()
    for key, value in details.items():
        caption += str(key) + ': ' + str(value) + '\n'
    if len(caption) > 1024:
        caption = caption[:1024]
        await event.reply('Notice: Caption too long, trimmed')
    caption = escape(caption, quote=False)

    for img in imgs:
        filetype = str(guess_type(img.url)[0])
        if filetype.startswith('image'):
            media.append(img.display_url)
        else:
            await event.reply('File is not image, try download option.')
            return
    await event.reply(caption, file=media)

@chat_action('document')
async def sendDocuments(event, imgs: List['Image'], chat_id=None):
    if not chat_id:  # send to current chat
        await event.reply(file=[img.path for img in imgs], force_document=True)
    else:
        await event.client.send_message(chat_id,
                                        file=[img.path for img in imgs],
                                        force_document=True)

def handleBadRequest(update, context, error):
    logger.info('BadRequest exception: ' + str(error))
    if 'Wrong file identifier/http url' in error.message or 'Failed to get http url content' in error.message:
        update.message.reply_text(
            'Failed to send image as photo, maybe the size is too big, '
            'consider using download option or try again.\n'
            f'Error: {error.message}')
    elif 'Group send failed' in error.message:
        update.message.reply_text(
            'Failed to send images because one of them is too large, '
            'consider using download option or try again.\n'
            f'Error: {error.message}')
    else:
        raise error

@retry
async def downloadImage(img: 'Image', session: aiohttp.ClientSession):
    async with session.get(img.url) as response:
        async with aiofiles.open(img.path, 'wb') as f:
            await f.write(await response.read())

async def downloadImages(imgs: List['Image'], headers=None):
    if headers is None:
        headers = dict()
    headers.update({'User-Agent': UA})
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    async with aiohttp.ClientSession(
            # connector=aiohttp.TCPConnector(verify_ssl=False),
            headers=headers,
            trust_env=True) as session:
        tasks = []
        for img in imgs:
            tasks.append(asyncio.create_task(downloadImage(img, session)))
        await asyncio.gather(*tasks)

def sanitizeFilename(name: str) -> str:
    # https://docs.microsoft.com/zh-cn/windows/win32/fileio/naming-a-file
    name = re.sub(r"[\"*/:<>?\\|]+", '_', name)  # reserved characters
    name = re.sub(r"[\t\n\r\f\v]+", ' ', name)
    name = re.sub(r"\u202E|\u200E|\u200F", '', name)  # RTL marks
    filename, ext = os.path.splitext(name)
    filename = filename.strip()
    if Path(filename).is_reserved():
        filename = '_' + filename
    name = filename + ext
    if len(name) > 255:
        name = filename[:255 - len(ext)] + ext
    return name

def getUrlsFromEvent(event) -> List[str]:
    entities = event.get_entities_text()
    urls = list()
    for entity in entities:
        if isinstance(entity[0], MessageEntityUrl):
            urls.append(entity[1])
        elif isinstance(entity[0], MessageEntityTextUrl):
            urls.append(entity[0].url)
    return urls

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run

class NazurinError(Exception):
    def __init__(self, msg):
        """Initialize with error message."""
        super().__init__(msg)
        self.msg = str(msg)

    def __str__(self):
        """Returns the string representation of this exception."""
        return self.msg
