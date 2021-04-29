from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from nazurin import bot, dp

from .api import Moebooru

moebooru = Moebooru()

@dp.message_handler(Command(['yandere']))
async def yandere_view(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /yandere POST_ID')
        return
    if post_id < 0:
        await message.reply('Invalid post id!')
        return
    illust = await moebooru.site('yande.re').view(post_id)
    await bot.sendIllust(illust, message)

@dp.message_handler(Command(['yandere_download']))
async def yandere_download(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /yandere_download POST_ID')
        return
    if post_id <= 0:
        await message.reply('Invalid post id!')
        return
    illust = await moebooru.site('yande.re').view(post_id)
    await illust.download()
    await bot.sendDocuments(illust, message)

@dp.message_handler(Command(['konachan']))
async def konachan_view(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /konachan POST_ID')
        return
    if post_id < 0:
        await message.reply('Invalid post id!')
        return
    illust = await moebooru.site('konachan.com').view(post_id)
    await bot.sendIllust(illust, message)

@dp.message_handler(Command(['konachan_download']))
async def konachan_download(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /konachan_download POST_ID')
        return
    if post_id <= 0:
        await message.reply('Invalid post id!')
        return
    illust = await moebooru.site('konachan.com').view(post_id)
    await illust.download()
    await bot.sendDocuments(illust, message)
