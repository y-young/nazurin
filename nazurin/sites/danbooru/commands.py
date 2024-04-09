from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from nazurin import bot, dp
from nazurin.utils.exceptions import InvalidCommandUsageError

from .api import Danbooru

danbooru = Danbooru()


@dp.message_handler(
    Command("danbooru"),
    args="POST_ID",
    description="View Danbooru post",
)
async def danbooru_view(message: Message, command: CommandObject):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("danbooru") from e
    if post_id <= 0:
        await message.reply("Invalid post id!")
        return
    illust = await danbooru.view(post_id)
    await bot.send_illust(illust, message)


@dp.message_handler(
    Command("danbooru_download"),
    args="POST_ID",
    description="Download Danbooru post",
)
async def danbooru_download(message: Message, command: CommandObject):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("danbooru_download") from e
    if post_id <= 0:
        await message.reply("Invalid post id!")
        return
    illust = await danbooru.view(post_id)
    await illust.download()
    await bot.send_docs(illust, message)
