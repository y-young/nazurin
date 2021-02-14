# -*- coding: utf-8 -*-
import shutil
import traceback
from typing import List

from aiogram.types import ChatActions, ContentType, Message, Update
from aiogram.utils.exceptions import TelegramAPIError

from nazurin import config, dp
from nazurin.utils import logger
from nazurin.utils.decorators import chat_action
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.filters import URLFilter

@dp.message_handler(commands=['start', 'help'])
@chat_action(ChatActions.TYPING)
async def show_help(message: Message):
    await message.reply('''
    小さな小さな賢将, can help you collect images from various sites.
    Commands:
    /ping - pong
    /pixiv <id> - view pixiv artwork
    /pixiv_download <id> - download pixiv artwork
    /danbooru <id> - view danbooru post
    /danbooru_download <id> - download danbooru post
    /yandere <id> - view yandere post
    /yandere_download <id> - download yandere post
    /konachan <id> - view konachan post
    /konachan_download <id> - download konachan post
    /bookmark <id> - bookmark pixiv artwork
    /clear_cache - clear download cache
    /help - get this help text
    PS: Send Pixiv/Danbooru/Yandere/Konachan/Twitter URL to download image(s)
    ''')

@dp.message_handler(commands=['ping'])
@chat_action(ChatActions.TYPING)
async def ping(message: Message):
    await message.reply('pong!')

@dp.message_handler(URLFilter(),
                    content_types=[ContentType.TEXT, ContentType.PHOTO])
async def update_collection(message: Message, urls: List[str]):
    try:
        await dp.bot.updateCollection(urls, message)
        await message.reply('Done!')
    except NazurinError as error:
        await message.reply(error.msg)

@dp.message_handler(commands=['clear_cache'])
async def clear_cache(message: Message):
    try:
        shutil.rmtree(config.TEMP_DIR)
        await message.reply("Cache cleared successfully.")
    except PermissionError:
        await message.reply("Permission denied.")
    except OSError as error:
        await message.reply(error.strerror)

@dp.errors_handler()
async def on_error(update: Update, error: Exception):
    try:
        raise error
    except Exception as error:
        logger.error('Update %s caused %s: %s', update, type(error), error)
        traceback.print_exc()
        if not isinstance(error, TelegramAPIError):
            await update.message.reply('Error: ' + str(error))
        return True

def main():
    dp.start()

if __name__ == '__main__':
    main()
