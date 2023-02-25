from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from nazurin import bot, dp

from .api import Danbooru

danbooru = Danbooru()


@dp.message_handler(Command(["danbooru"]))
async def danbooru_view(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply("Usage: /danbooru POST_ID")
        return
    if post_id <= 0:
        await message.reply("Invalid post id!")
        return
    illust = await danbooru.view(post_id)
    await bot.send_illust(illust, message)


@dp.message_handler(Command(["danbooru_download"]))
async def danbooru_download(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply("Usage: /danbooru_download POST_ID")
        return
    if post_id <= 0:
        await message.reply("Invalid post id!")
        return
    illust = await danbooru.view(post_id)
    await illust.download()
    await bot.send_docs(illust, message)
