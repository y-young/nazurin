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
import tenacity
from aiogram.types import ChatActions, InputMediaPhoto, Message

from nazurin.config import RETRIES, TEMP_DIR, UA

if TYPE_CHECKING:
    from nazurin.models import Image

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger('nazurin')
retry = tenacity.retry(stop=tenacity.stop_after_attempt(RETRIES),
                       before=tenacity.before_log(logger, logging.INFO))

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def chat_action(action: str):
    """Sends `action` while processing."""
    def decorator(func):
        @wraps(func)
        async def wrapped_func(message: Message, *args, **kwargs):
            await ChatActions._do(action)
            return await func(message, *args, **kwargs)

        return wrapped_func

    return decorator

@chat_action(ChatActions.UPLOAD_PHOTO)
async def sendPhotos(message: Message, imgs: List['Image'], details=None):
    if details is None:
        details = dict()
    media = list()
    if len(imgs) > 10:
        # TODO
        imgs = imgs[:10]
        await message.reply('Notice: Too many pages, sending only 10 of them')

    caption = str()
    for key, value in details.items():
        caption += str(key) + ': ' + str(value) + '\n'
    if len(caption) > 1024:
        caption = caption[:1024]
        await message.reply('Notice: Caption too long, trimmed')
    caption = escape(caption, quote=False)

    for img in imgs:
        filetype = str(guess_type(img.url)[0])
        if filetype.startswith('image'):
            media.append(InputMediaPhoto(img.display_url))
        else:
            await message.reply('File is not image, try download option.')
            return
    media[0].caption = caption
    await message.reply_media_group(media)

@chat_action(ChatActions.UPLOAD_DOCUMENT)
async def sendDocuments(message: Message, imgs: List['Image'], chat_id=None):
    message_id = message.message_id
    if not chat_id:
        chat_id = message.chat.id
    else:
        message_id = None  # Sending to channel, no message to reply
    for img in imgs:
        await message.bot.send_document(chat_id,
                                        open(img.path, 'rb'),
                                        reply_to_message_id=message_id)

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

def getUrlsFromMessage(message: Message) -> List[str]:
    if message.entities:
        entities = message.entities
        text = message.text
    elif message.caption_entities:
        entities = message.caption_entities
        text = message.caption
    else:
        return []
    # Telegram counts entity offset and length in UTF-16 code units
    text = text.encode('utf-16-le')
    urls = list()
    for item in entities:
        if item.type == 'text_link':
            urls.append(item.url)
        elif item.type == 'url':
            offset = item.offset
            length = item.length
            urls.append(text[offset * 2:(offset + length) *
                             2].decode('utf-16-le'))
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
