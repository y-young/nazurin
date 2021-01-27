# -*- coding: utf-8 -*-
import asyncio
import shutil
import traceback

from telethon import TelegramClient, events

import config
from sites import SiteManager
from storage import Storage
from utils import (NazurinError, chat_action, getUrlsFromEvent, logger,
                   sendDocuments)

bot = TelegramClient('bot', config.API_ID,
                     config.API_HASH).start(bot_token=config.TOKEN)
sites = SiteManager()
storage = Storage()

@bot.on(events.NewMessage(incoming=True))
async def user_filter(event):
    if event.chat_id in config.ADMIN_ID + config.GROUP_ID\
        or event.sender_id in config.ADMIN_ID\
        or (await event.get_sender()).username in config.ADMIN_USERNAME:
        return
    else:
        raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/help'))
async def show_help(event):
    await event.reply('''
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
    raise event.StopPropagation

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await show_help(event)

@bot.on(events.NewMessage(pattern='/ping'))
async def ping(event):
    await event.reply('pong!')
    raise event.StopPropagation

@bot.on(events.NewMessage(incoming=True))
async def update_collection(event):
    urls = getUrlsFromEvent(event)
    if not urls:
        return
    result = sites.match(urls)
    if not result:
        await event.reply('Error: No source matched')
        raise event.StopPropagation
    logger.info('Collection update: site=%s, match=%s', result['site'],
                result['match'].groups())
    # Forward to gallery & Save to album
    await event.message.forward_to(config.GALLERY_ID)

    try:
        imgs = sites.handle_update(result)
        await sendDocuments(event, imgs, chat_id=config.ALBUM_ID)
        storage.store(imgs)
        await event.reply('Done!')
    except NazurinError as error:
        await event.reply(error.msg)
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/clear_cache'))
async def clear_cache(event):
    try:
        shutil.rmtree('./downloads')
        await event.reply("downloads directory cleared successfully.")
    except PermissionError:
        await event.reply("Permission denied.")
    except OSError as error:
        await event.reply(error.strerror)

def main():
    global sites, storage, bot
    sites.load()
    sites.register_commands(bot)
    storage.load()
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
