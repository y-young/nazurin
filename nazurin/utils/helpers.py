import os
import pathlib
import re
from datetime import datetime
from html import escape
from mimetypes import guess_type
from pathlib import Path
from string import capwords
from typing import Callable, List

import aiofiles
import aiofiles.os
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

def sanitize_path_segment(segment: str) -> str:
    """
    Remove invalid characters from a path segment. e.g. `/\\<>:"|?*`.
    """

    segment = re.sub(r"[\"*/:<>?\\|]+", '_', segment)  # reserved characters
    segment = re.sub(r"[\t\n\r\f\v]+", ' ', segment)
    segment = re.sub(r"\u202E|\u200E|\u200F", '', segment)  # RTL marks
    return segment

def sanitize_filename(name: str) -> str:
    # https://docs.microsoft.com/zh-cn/windows/win32/fileio/naming-a-file
    name = sanitize_path_segment(name)
    filename, ext = os.path.splitext(name)
    filename = filename.strip()
    if Path(filename).is_reserved():
        filename = '_' + filename
    name = filename + ext
    if len(name) > 255:
        name = filename[:255 - len(ext)] + ext
    return name

def sanitize_path(
    path: os.PathLike,
    sanitize: Callable[[str],
                       str] = sanitize_path_segment) -> pathlib.PurePath:
    """
    Remove invalid characters from a path.
    Apply `sanitize` function to every segment and join them as PurePath.
    """

    segments = pathlib.PurePath(path).parts
    segments = [
        sanitize(segment) if segment != "/" else segment
        for segment in segments
    ]
    return pathlib.PurePath(*segments)

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

async def ensure_existence_async(path: str):
    if not await aiofiles.os.path.exists(path):
        await aiofiles.os.makedirs(path)

def snake_to_pascal(name: str):
    """Convert snake_case to PascalCase"""
    return capwords(name.replace('_', ' ')).replace(' ', '')

async def read_by_chunks(path: str, chunk_size: int = 4 * 1024 * 1024):
    async with aiofiles.open(path, 'rb') as f:
        chunk = await f.read(chunk_size)
        while chunk:
            yield chunk
            chunk = await f.read(chunk_size)

def fromisoformat(date: str):
    """
    A polyfill for `datetime.fromisoformat` before Python 3.11.

    Prior to Python 3.11, `datetime.fromisoformat` does not recognize
    UTC timezone represented as 'Z'.

    https://docs.python.org/3/library/datetime.html?highlight=fromisoformat#datetime.datetime.fromisoformat
    """

    if date.endswith('Z'):
        date = date[:-1] + '+00:00'
    return datetime.fromisoformat(date)

def fromasctimeformat(date: str):
    """
    Convert a string in an asctime-like format (but with timezone)
    to datetime object. e.g. "Sat Oct 22 08:45:05 -0500 2022"
    """

    return datetime.strptime(date, '%a %b %d %H:%M:%S %z %Y')
