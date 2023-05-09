from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from nazurin import bot, dp
from nazurin.utils.exceptions import InvalidCommandUsage

from .api import Zerochan

api = Zerochan()


@dp.message_handler(
    Command(["zerochan"]), args="POST_ID", description="View Zerochan post"
)
async def zerochan_view(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsage("zerochan") from e
    if post_id < 0:
        await message.reply("Invalid post id!")
        return
    illust = await api.view(post_id)
    await bot.send_illust(illust, message)


@dp.message_handler(
    Command(["zerochan_download"]), args="POST_ID", description="Download Zerochan post"
)
async def zerochan_download(message: Message, command: Command.CommandObj):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsage("zerochan_download") from e
    if post_id <= 0:
        await message.reply("Invalid post id!")
        return
    illust = await api.view(post_id)
    await illust.download()
    await bot.send_docs(illust, message)
