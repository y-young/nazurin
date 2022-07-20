from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from nazurin import bot, dp

from .api import Zerochan

api = Zerochan()

@dp.message_handler(Command(['zerochan']))
async def zerochan_view(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /zerochan POST_ID')
        return
    if post_id < 0:
        await message.reply('Invalid post id!')
        return
    illust = await api.view(post_id)
    await bot.send_illust(illust, message)

@dp.message_handler(Command(['zerochan_download']))
async def zerochan_download(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /zerochan_download POST_ID')
        return
    if post_id <= 0:
        await message.reply('Invalid post id!')
        return
    illust = await api.view(post_id)
    await illust.download()
    await bot.send_docs(illust, message)
