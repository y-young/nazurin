# -*- coding: utf-8 -*-
import shutil
import traceback
from html import escape

from aiogram.dispatcher.filters import IDFilter
from aiogram.types import ChatActions, Message, Update
from aiogram.utils.exceptions import TelegramAPIError
from aiohttp import ClientResponseError

from nazurin import config, dp
from nazurin.utils import logger
from nazurin.utils.decorators import chat_action
from nazurin.utils.exceptions import NazurinError

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
        shutil.rmtree(config.TEMP_DIR)
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
        await update.message.reply(
            f'Response Error: {error.status} {error.message}')
    except NazurinError as error:
        await update.message.reply(error.msg)
    except Exception as error:
        logger.error('Update %s caused %s: %s', update, type(error), error)
        traceback.print_exc()
        if not isinstance(error, TelegramAPIError):
            await update.message.reply('Error: ' +
                                       escape(str(error), quote=False))
    return True

def main():
    dp.start()

if __name__ == '__main__':
    main()
