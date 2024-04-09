from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from nazurin import bot, dp
from nazurin.utils.exceptions import InvalidCommandUsageError

from .api import Twitter

twitter = Twitter()


@dp.message_handler(Command("twitter"), args="STATUS_ID", description="View tweet")
async def twitter_view(message: Message, command: CommandObject):
    try:
        status_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("twitter") from e
    if status_id < 0:
        await message.reply("Invalid status id.")
        return
    illust = await twitter.fetch(status_id)
    await bot.send_illust(illust, message)


@dp.message_handler(
    Command("twitter_download"),
    args="STATUS_ID",
    description="Download tweet",
)
async def twitter_download(message: Message, command: CommandObject):
    try:
        status_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("twitter_download") from e
    if status_id < 0:
        await message.reply("Invalid status id.")
        return
    illust = await twitter.fetch(status_id)
    await illust.download()
    await bot.send_docs(illust, message)
