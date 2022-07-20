import os
import re
from html import escape
from mimetypes import guess_type
from pathlib import Path
from string import capwords
from typing import List

import aiofiles
from aiogram.types import Message
from aiogram.utils.exceptions import (BadRequest, InvalidHTTPUrlContent,
                                      WrongFileIdentifier)
from nazurin.models import Caption

from . import logger

async def handle_bad_request(message: Message, error: BadRequest):
    logger.error('BadRequest exception: %s', error)
    if not message:
        return
    if isinstance(error, (WrongFileIdentifier, InvalidHTTPUrlContent)):
        await message.reply(
            'Failed to send image as photo, maybe the size is too big, '
            'consider using download option or try again.\n'
            f'Message: {message.text}\n'
            f'Error: {error}')
    elif 'Group send failed' in str(error):
        await message.reply(
            'Failed to send images because one of them is too large, '
            'consider using download option or try again.\n'
            f'Message: {message.text}\n'
            f'Error: {error}')
    else:
        raise error

def sanitize_filename(name: str) -> str:
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

def sanitize_caption(caption: Caption) -> str:
    content = caption.text
    if len(content) > 1024:
        content = content[:1024]
    content = escape(content, quote=False)
    return content

def get_urls_from_message(message: Message) -> List[str]:
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

def is_image(url: str) -> bool:
    """
    Guess if a file is image by extension
    """

    filetype = str(guess_type(url)[0])
    return filetype.startswith('image')

def ensure_existence(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def snake_to_pascal(name: str):
    """Convert snake_case to PascalCase"""
    return capwords(name.replace('_', ' ')).replace(' ', '')

async def read_by_chunks(path: str, chunk_size: int = 4 * 1024 * 1024):
    async with aiofiles.open(path, 'rb') as f:
        chunk = await f.read(chunk_size)
        while chunk:
            yield chunk
            chunk = await f.read(chunk_size)
