from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from nazurin import bot, dp

from .api import Twitter

twitter = Twitter()


@dp.message_handler(Command(["twitter"]))
async def twitter_view(message: Message, command: Command.CommandObj):
    try:
        status_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply("Usage: /twitter STATUS_ID")
        return
    if status_id < 0:
        await message.reply("Invalid status id.")
        return
    illust = await twitter.fetch(status_id)
    await bot.send_illust(illust, message)


@dp.message_handler(Command(["twitter_download"]))
async def twitter_download(message: Message, command: Command.CommandObj):
    try:
        status_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply("Usage: /twitter_download STATUS_ID")
        return
    if status_id < 0:
        await message.reply("Invalid status id.")
        return
    illust = await twitter.fetch(status_id)
    await illust.download()
    await bot.send_docs(illust, message)
