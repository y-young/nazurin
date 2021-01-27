import asyncio
import logging
import os
import re
from functools import wraps
from html import escape
from mimetypes import guess_type
from pathlib import Path
from shutil import copyfileobj

import requests
from requests.adapters import HTTPAdapter
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl

from config import RETRIES, TEMP_DIR, UA

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger('nazurin')

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
async def sendPhotos(event, imgs, details=None):
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
async def sendDocuments(event, imgs, chat_id=None):
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

def downloadImages(imgs, headers=None):
    if headers is None:
        headers = dict()
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    with requests.Session() as session:
        session.headers.update({'User-Agent': UA})
        session.mount('https://', HTTPAdapter(max_retries=RETRIES))
        for img in imgs:
            response = session.get(img.url, stream=True, timeout=5).raw
            with open(img.path, 'wb') as f:
                copyfileobj(response, f)

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

def getUrlsFromEvent(event) -> list:
    entities = event.get_entities_text()
    urls = list()
    for entity in entities:
        if isinstance(entity[0], MessageEntityUrl):
            urls.append(entity[1])
        elif isinstance(entity[0], MessageEntityTextUrl):
            urls.append(entity[0].url)
    return urls

class NazurinError(Exception):
    def __init__(self, msg):
        """Initialize with error message."""
        super().__init__(msg)
        self.msg = str(msg)

    def __str__(self):
        """Returns the string representation of this exception."""
        return self.msg
