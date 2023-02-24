# -*- coding: utf-8 -*-
import asyncio
import os
import shutil
import traceback

from aiogram.dispatcher.filters import IDFilter
from aiogram.types import ChatActions, Message, Update
from aiogram.utils.exceptions import TelegramAPIError
from aiohttp import ClientResponseError

from nazurin import config, dp
from nazurin.utils import logger
from nazurin.utils.decorators import Cache, chat_action
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import format_error

@dp.message_handler(commands=['start', 'help'])
@chat_action(ChatActions.TYPING)
async def show_help(message: Message):
    await message.reply('''
    小さな小さな賢将, can help you collect images from various sites.
    Commands:
    /ping - pong
    /pixiv ARTWORK_ID - view pixiv artwork
    /pixiv_download ARTWORK_ID - download pixiv artwork
    /danbooru POST_ID - view danbooru post
    /danbooru_download POST_ID - download danbooru post
    /yandere POST_ID - view yandere post
    /yandere_download POST_ID - download yandere post
    /konachan POST_ID - view konachan post
    /konachan_download POST_ID - download konachan post
    /pixiv_bookmark ARTWORK_ID - bookmark pixiv artwork
    /clear_cache - clear download cache
    /help - get this help text
    PS: Send Pixiv/Danbooru/Yandere/Konachan/Twitter URL to download image(s)
    ''')

@dp.message_handler(commands=['ping'])
@chat_action(ChatActions.TYPING)
async def ping(message: Message):
    await message.reply('pong!')

@dp.message_handler(IDFilter(config.ADMIN_ID), commands=['clear_cache'])
async def clear_cache(message: Message):
    try:
        if os.path.exists(config.TEMP_DIR):
            shutil.rmtree(config.TEMP_DIR)
        Cache.clear()
        await message.reply("Cache cleared successfully.")
    except PermissionError:
        await message.reply("Permission denied.")
    except OSError as error:
        await message.reply(error.strerror)

@dp.errors_handler()
async def on_error(update: Update, exception: Exception):
    try:
        raise exception
    except ClientResponseError as error:
        traceback.print_exc()
        await update.message.reply(
            f'Response Error: {error.status} {error.message}')
    except NazurinError as error:
        await update.message.reply(error.msg)
    except asyncio.TimeoutError:
        traceback.print_exc()
        await update.message.reply('Error: Timeout, please try again.')
    except Exception as error:  # pylint: disable=broad-except
        logger.exception('Update {} caused {}: {}', update, type(error), error)
        if not isinstance(error, TelegramAPIError):
            await update.message.reply(f'Error: {format_error(error)}')

    return True

def main():
    dp.start()

if __name__ == '__main__':
    main()
